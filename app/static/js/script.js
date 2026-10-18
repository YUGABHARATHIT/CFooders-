/* FoodieGo — small frontend enhancements */
document.addEventListener("DOMContentLoaded", () => {
    // Automatically hide Django messages after a short delay.
    document.querySelectorAll(".message").forEach((message) => {
        window.setTimeout(() => {
            message.style.transition = "opacity .35s ease, transform .35s ease";
            message.style.opacity = "0";
            message.style.transform = "translateY(-5px)";
            window.setTimeout(() => message.remove(), 400);
        }, 4500);
    });

    // Avoid accidental double submission of checkout forms.
    document.querySelectorAll(".checkout-form").forEach((form) => {
        form.addEventListener("submit", () => {
            const button = form.querySelector('button[type="submit"]');
            if (button && form.checkValidity()) {
                button.disabled = true;
                button.textContent = "Placing order...";
            }
        });
    });

    // Confirm before submitting a Remove action from the cart.
    document.querySelectorAll(".cart-item form").forEach((form) => {
        const quantity = form.querySelector('input[name="quantity"][value="0"]');
        if (quantity) {
            form.addEventListener("submit", (event) => {
                if (!window.confirm("Remove this food item from your cart?")) {
                    event.preventDefault();
                }
            });
        }
    });

    // Basic client-side phone input cleanup: allow digits, spaces, +, - and parentheses.
    const phoneInput = document.querySelector("#phone");
    if (phoneInput) {
        phoneInput.addEventListener("input", () => {
            phoneInput.value = phoneInput.value.replace(/[^0-9+\-()\s]/g, "");
        });
    }
});
