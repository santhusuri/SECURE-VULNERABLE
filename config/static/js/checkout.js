// Checkout JS for Stripe payment
const stripe = Stripe(STRIPE_PUBLIC_KEY);
const elements = stripe.elements();
const card = elements.create("card");
card.mount("#card-element");

const form = document.getElementById("payment-form");
form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const { paymentIntent, error } = await stripe.confirmCardPayment(CLIENT_SECRET, {
    payment_method: { card: card }
  });

  if (error) {
    alert(error.message);
  } else {
    // ✅ Call backend to create order with paymentIntent.id
    fetch(CREATE_ORDER_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": CSRF_TOKEN
      },
      body: JSON.stringify({ payment_intent_id: paymentIntent.id })
    })
    .then(res => res.json())
    .then(data => {
      if (data.payment_intent_id) {
        // Redirect to success page using Stripe PI ID
        window.location.href = ORDER_SUCCESS_URL.replace("PLACEHOLDER", data.payment_intent_id);
      } else {
        alert("Order creation failed: " + (data.error || "Unknown error"));
      }
    })
    .catch(err => alert("Error creating order: " + err));
  }
});
