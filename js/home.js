
        document.addEventListener('DOMContentLoaded', () => {
            cart = { quantity: 0, contents: [] }; 
            sessionStorage.removeItem('cart'); 
            
            
           
            updateCartContents(cart.contents);
                    
            let itemCount = 0; // Initialize itemCount
            let cartTotal = 0; 
            
            
            function updateCartData() {
                sessionStorage.setItem('cart', JSON.stringify(cart));
            }


            let disabledButtons = {}; 

            function handleSubmit(event) { //submits cart content
                event.preventDefault();
                const form = event.target;
                const productId = form.product_id.value;
                const productName = form.product_name.value;
                const productPrice = parseFloat(form.product_price.value);


                const existingProduct = cart.contents.find(item => item.id === productId);
                    if (existingProduct) {
                        alert('You can only select one item per product.');
                        return;
                    }

                cart.contents.push({ id: productId, name: productName, price: productPrice, quantity: 1 });
                cart.quantity += 1;
                itemCount += 1;
                cartTotal += productPrice;


                const button = form.querySelector('button');
                    button.disabled = true;
                    button.style.backgroundColor = '#d3d3d3'; // Light grey
                    button.style.color = '#a9a9a9'; // Darker grey
                    button.textContent = 'Added';

                    disabledButtons[productId] = button;

                    
                    updateCartData();
                    updateCartQuantity(cart.quantity);
                    updateCartContents(cart.contents);
               
                    
            }
    
            function updateCartQuantity(quantity) {
                document.getElementById('cart-item-count').textContent = quantity;
                }
           
            
            function updateCartContents(cartContents) {
                const cartItemsElement = document.getElementById('cart-items');
                const cartTotalSidebarElement = document.getElementById('cart-total-sidebar');

                cartItemsElement.innerHTML = '';

                let total = 0;

                cartContents.forEach(item => {
                    total += item.price * item.quantity;
                    const listItem = document.createElement('li');
                    listItem.innerHTML = `
                        <button class="remove-btn" onclick="removeFromCart('${item.id}')">&#x2715;</button>
                        ${item.name} - $${item.price}  
                    `;
                    cartItemsElement.appendChild(listItem);
                });

                cartTotalSidebarElement.textContent = `Total: $${total.toFixed(2)}`;
            }

            function updateCartTotal() {
                let total = cart.contents.reduce((sum, item) => sum + item.price * item.quantity, 0);
                document.getElementById('cart-total').innerText = `Total: $${total.toFixed(2)}`;
            }
        
            

        function updateQuantity(productId, change) {
            const product = cart.contents.find(item => item.id === productId);
            if (product) {
                product.quantity += change;
                if (product.quantity <= 0) {
                    removeFromCart(productId);
                } else {
                    cart.quantity += change;
                    itemCount += change;
                    cartTotal += product.price * change;

                    updateCartQuantity(cart.quantity);
                    updateCartContents(cart.contents);
                    
                }
            }
        }
            function toggleCartSidebar() {
                const cartSidebar = document.getElementById('cart-sidebar');
                
                if (cartSidebar.classList.contains('active')) {
                    cartSidebar.classList.remove('active');
                } else {
                    cartSidebar.classList.add('active');
                }
            }

            window.removeFromCart = function(productId) {
            const productIndex = cart.contents.findIndex(item => item.id === productId);
            if (productIndex > -1) {
                const product = cart.contents[productIndex];
                cart.quantity -= product.quantity;
                cart.contents.splice(productIndex, 1);

                // Re-enable the button if it was disabled
                if (disabledButtons[productId]) {
                    const button = disabledButtons[productId];
                    button.disabled = false;
                    button.style.backgroundColor = ''; 
                    button.style.color = ''; 
                    button.textContent = 'Add to Cart'; 
                }

                updateCartData();
                updateCartQuantity(cart.quantity);
                updateCartContents(cart.contents);
                updateCartTotal()
               

            }
        };

        function clearCart() {
            cart = { quantity: 0, contents: [] }; 
            sessionStorage.removeItem('cart'); 
        
            Object.keys(disabledButtons).forEach(productId => {
                const button = disabledButtons[productId];
                button.disabled = false;
                button.style.backgroundColor = ''; 
                button.style.color = ''; 
                button.textContent = 'Add to Cart';
            });
            disabledButtons = {};
        
            
            updateCartData(); 
            updateCartQuantity(cart.quantity);
            updateCartContents(cart.contents);
            updateCartTotal();
        }
        
        const clearCartButton = document.getElementById('clear-cart');
        if (clearCartButton) {
            clearCartButton.addEventListener('click', clearCart);
            
        }


            document.querySelectorAll('form').forEach(form => {
                form.addEventListener('submit', handleSubmit);
            });

            window.toggleCartSidebar = toggleCartSidebar;
            window.updateQuantity = updateQuantity;

            window.goToCheckout = function() {
                if (cart.contents.length === 0) {
                    alert('Your cart is empty. Please add items to the cart before proceeding to checkout.');
                    return;
                }   
                window.location.href = 'checkout';
            }
            

        });
        document.addEventListener('DOMContentLoaded', () => {
            const popupOverlay = document.getElementById('popupOverlay');
            const popups = document.querySelectorAll('.popup');

            function openPopup(popup) {
                if (popup == null) return;
                popup.classList.add('active');
                popupOverlay.classList.add('active');
            }

            function closePopup(popup) {
                if (popup == null) return;
                popup.classList.remove('active');
                popupOverlay.classList.remove('active');
            }

            // Open the popup when button is clicked
            document.addEventListener('click', (event) => {
                if (event.target.classList.contains('openPopup')) {
                    const popupId = event.target.getAttribute('data-popup-id');
                    const popup = document.getElementById(popupId);
                    openPopup(popup);
                }
            });

            // Close the popup when close button is clicked
            document.addEventListener('click', (event) => {
                if (event.target.matches('[data-close-button]')) {
                    const popup = event.target.closest('.popup');
                    closePopup(popup);
                }
            });

            // Close the popup when clicking outside of popup content
            popupOverlay.addEventListener('click', () => {
                popups.forEach(popup => {
                    closePopup(popup);
                });
            });
        });


