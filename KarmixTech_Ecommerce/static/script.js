
// script.js

// Close the menu when clicking outside of it

const list = document.querySelector(".nav");
const hamburger = document.querySelector(".fa-bars");

hamburger.addEventListener("click", () => {
  hamburger.classList.toggle("fa-x");
  list.classList.toggle("nav-active");
});


document.querySelectorAll(".link").forEach(link => {
  link.addEventListener("click", function (event) {
    event.preventDefault();
    const href = this.getAttribute("href");

    if (href.startsWith("#")) {
      const targetSection = document.querySelector(href);
      if (targetSection) {
        targetSection.scrollIntoView({ behavior: "smooth" });
      } else {
        console.warn("Target section not found for", href);
      }
    } else {
      window.location.href = href; // open new page
    }
  });
});

document.addEventListener('DOMContentLoaded', function () {
    // Fetch initial cart count
    fetch('/cart_count')
        .then(res => res.json())
        .then(data => {
            document.getElementById('cart-count').innerText = data.count;
        });

    // Handle Add to Cart buttons
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function () {
            const card = this.closest('.card');
            const product_name = card.querySelector('.title').innerText;
            const price = parseFloat(card.querySelector('.price').innerText.replace('₹', ''));
            const image = card.querySelector('img').getAttribute('src');

            fetch('/add-to-cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    product_name,
                    price,
                    image
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                   alert("✅ Product added to cart!");
                    // ✅ Instantly update cart count
                    document.getElementById('cart-count').innerText = data.cart_count;
                    console.log("✅ Added to cart:", product_name);
                } else {
                    alert("❌ " + data.error);
                }
            })
            .catch(err => {
                console.error('❌ Error adding to cart:', err);
            });
        });
    });
});

  document.addEventListener("DOMContentLoaded", function () {
    const profileIcon = document.getElementById("profile-icon");
    const dropdown = document.getElementById("profile-dropdown");

    profileIcon.addEventListener("click", function (e) {
      e.preventDefault();
      dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", function (event) {
      if (!profileIcon.contains(event.target) && !dropdown.contains(event.target)) {
        dropdown.style.display = "none";
      }
    });
  });