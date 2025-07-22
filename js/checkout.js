document.addEventListener('DOMContentLoaded', () => {
    let cart = JSON.parse(sessionStorage.getItem('cart')) || { quantity: 0, contents: [] };


    function updateCartData() {
        sessionStorage.setItem('cart', JSON.stringify(cart));
    }

    function updateCartContents() {
        const cartItemsElement = document.getElementById('cart-items');
        const cartTotalElement = document.getElementById('cart-total-sidebar');


        // Update main cart section
        cartItemsElement.innerHTML = '';
        let total = 0;

        cart.contents.forEach(item => {
            total += item.price * item.quantity;
            const listItem = document.createElement('li');
            listItem.innerHTML = `
                <span>${item.name} - $${item.price.toFixed(2)}</span>
                <button class="cart-remove-button" onclick="removeFromCart('${item.id}')">&#x2715;</button>
            `;
            cartItemsElement.appendChild(listItem);
        });

        cartTotalElement.textContent = `Total: $${total.toFixed(2)}`;

        // Update modal section
    }

    function toggleCartSidebar() {
        const cartSidebar = document.getElementById('cart-sidebar');
        if (cartSidebar) {
            cartSidebar.classList.toggle('');
        }
    }

    function updateCartQuantity(quantity) {
        const quantityElement = document.getElementById('cart-item-count');
        if (quantityElement) {
            quantityElement.textContent = quantity;
        }
    }

    function updateCartTotal() {
        let total = cart.contents.reduce((sum, item) => sum + item.price * item.quantity, 0);
        document.getElementById('cart-total').innerText = `Total: $${total.toFixed(2)}`;
    }

    function goBack() {
        updateCartData();
        window.location.href = '/home';
    }



    window.removeFromCart = function(productId) {
        const productIndex = cart.contents.findIndex(item => item.id === productId);
        if (productIndex > -1) {
            const product = cart.contents[productIndex];
            cart.quantity -= product.quantity;
            cart.contents.splice(productIndex, 1);

            updateCartData();
            updateCartQuantity(cart.quantity);
            updateCartContents(cart.contents);
            updateCartTotal();
        }
    };

    window.goToCheckout2 = function() {
        window.location.href = 'checkout_details';
    }

    window.toggleCartSidebar = toggleCartSidebar;

    const clearCartButton = document.getElementById('clear-cart');
    if (clearCartButton) {
        clearCartButton.addEventListener('click', () => {
            cart = { quantity: 0, contents: [] };
            sessionStorage.removeItem('cart');
            updateCartData();
            updateCartQuantity(cart.quantity);
            updateCartContents();
            updateCartTotal();
        });
    }

    const backButton = document.getElementById('back-button');
    if (backButton) {
        backButton.addEventListener('click', goBack);

    }

    updateCartContents();
    updateCartTotal();
});




















document.addEventListener('DOMContentLoaded', () => {
    let cart = JSON.parse(sessionStorage.getItem('cart')) || { quantity: 0, contents: [] };

    function updateCartData() {
        sessionStorage.setItem('cart', JSON.stringify(cart));
    }

    function updateCartContents() {
        const cartItemsElement = document.getElementById('cart-items');
        const cartTotalElement = document.getElementById('cart-total');

        if (!cartItemsElement || !cartTotalElement) return; // Prevent errors if elements are missing

        cartItemsElement.innerHTML = '';
        let total = 0;

        cart.contents.forEach(item => {
            total += item.price * item.quantity;
            const listItem = document.createElement('li');
            listItem.innerHTML = `
                <span>${item.name} - $${item.price.toFixed(2)} (x${item.quantity})</span>
                <button class="cart-remove-button" onclick="removeFromCart('${item.id}')">&#x2715;</button>
            `;
            cartItemsElement.appendChild(listItem);
        });

        cartTotalElement.textContent = `Total: $${total.toFixed(2)}`;
    }

    function updateCartQuantity(quantity) {
        const quantityElement = document.getElementById('cart-item-count');
        if (quantityElement) {
            quantityElement.textContent = quantity > 0 ? `(${quantity})` : '';
        }
    }

    function updateCartTotal() {
        let total = cart.contents.reduce((sum, item) => sum + item.price * item.quantity, 0);
        const totalElement = document.getElementById('cart-total');
        if (totalElement) {
            totalElement.innerText = `Total: $${total.toFixed(2)}`;
        }
    }

    function goBack() {
        updateCartData();
        window.location.href = '/home';
    }

    window.removeFromCart = function (productId) {
        const productIndex = cart.contents.findIndex(item => item.id === productId);
        if (productIndex > -1) {
            const product = cart.contents[productIndex];
            cart.quantity -= product.quantity;
            cart.contents.splice(productIndex, 1);

            updateCartData();
            updateCartQuantity(cart.quantity);
            updateCartContents();
            updateCartTotal();
        }
    };

    window.goToCheckout = function () {
        window.location.href = 'checkout_details';
    };

    const clearCartButton = document.getElementById('clear-cart');
    if (clearCartButton) {
        clearCartButton.addEventListener('click', () => {
            cart = { quantity: 0, contents: [] };
            sessionStorage.removeItem('cart');
            updateCartData();
            updateCartQuantity(cart.quantity);
            updateCartContents();
            updateCartTotal();
        });
    }

    const backButton = document.getElementById('back-button');
    if (backButton) {
        backButton.addEventListener('click', goBack);
    }

    // Initial update
    updateCartContents();
    updateCartTotal();
});
