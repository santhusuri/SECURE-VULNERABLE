# monitoring/management/commands/tail_suricata.py
import time
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from monitoring.models import Incident
from monitoring.utils import add_blacklist_entry, block_ip_system, revoke_session_on_project_a

class Command(BaseCommand):
    help = "Tail Suricata eve.json and ingest alerts into Incident model"

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="Path to eve.json", default=getattr(settings, "SURICATA_EVE_PATH", "/var/log/suricata/eve.json"))
        parser.add_argument("--sleep", type=float, help="Sleep seconds between polls", default=0.5)
        parser.add_argument("--blacklist", action="store_true", help="Automatically add offending IPs to Blacklist and attempt system block")

    def handle(self, *args, **options):
        path = options["path"]
        sleep = options["sleep"]
        do_blacklist = options["blacklist"]

        try:
            f = open(path, "r")
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {path}"))
            return

        # Seek to end of file (start watching new alerts only)
        f.seek(0, 2)

        self.stdout.write(self.style.SUCCESS(f"Tailing {path} ..."))
        while True:
            line = f.readline()
            if not line:
                time.sleep(sleep)
                continue

            try:
                obj = json.loads(line.strip())
            except Exception:
                continue

            if obj.get("event_type") != "alert":
                continue

            alert = obj.get("alert", {})
            signature = alert.get("signature", "suricata_alert")
            src_ip = obj.get("src_ip") or obj.get("src_ip", obj.get("flow", {}).get("src_ip", "0.0.0.0"))

            # Create incident
            inc = Incident.objects.create(
                attack_type="suricata_alert",
                event_data=signature,
                ip_address=src_ip,
                action_taken="Suricata alert logged",
                suricata_raw=obj
            )

            self.stdout.write(self.style.WARNING(f"Logged alert {signature} from {src_ip}"))

            if do_blacklist:
                created, entry = add_blacklist_entry(src_ip, reason=f"Suricata: {signature}")
                ok, msg = block_ip_system(src_ip)
                ok2, msg2 = revoke_session_on_project_a(src_ip)
                inc.action_taken = f"blacklist_created={created}; iptables={msg}; revoke_msg={msg2}"
                inc.save()
                self.stdout.write(self.style.SUCCESS(f"AIRS actions for {src_ip}: {inc.action_taken}"))
