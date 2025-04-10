function updateQuantity(productId, change) {
    const quantityInput = document.getElementById(`quantity-${productId}`);
    const currentQuantity = parseInt(quantityInput.value);
    const newQuantity = currentQuantity + change;
    
    if (newQuantity >= 0) {
        if (newQuantity === 0) {
            // If quantity becomes 0, remove the item
            removeFromCart(productId);
        } else {
            // Get the product element and its details
            const productElement = document.querySelector(`[data-product-id="${productId}"]`);
            const priceText = productElement.querySelector('p').textContent;
            const price = parseInt(priceText.replace('Giá: ', '').replace('đ', ''));
            
            // Create form data
            const formData = new FormData();
            formData.append('product_id', productId);
            formData.append('quantity', newQuantity);
            formData.append('price', price);
            
            // Send POST request
            fetch('/update-cart', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Update quantity input
                    quantityInput.value = newQuantity;
                    
                    // Update total price
                    const totalElement = document.getElementById('total-price');
                    if (totalElement) {
                        totalElement.textContent = data.total + 'đ';
                    }
                    
                    // Update cart count in header if it exists
                    const cartCount = document.getElementById('cart-count');
                    if (cartCount) {
                        cartCount.textContent = data.cart_count;
                    }
                } else {
                    console.error('Failed to update cart:', data.message);
                }
            })
            .catch(error => {
                console.error('Error updating cart:', error);
                // Revert the quantity if the update failed
                quantityInput.value = currentQuantity;
            });
        }
    }
}

function removeFromCart(productId) {
    // Create form data
    const formData = new FormData();
    formData.append('product_id', productId);
    
    fetch('/remove-from-cart', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Remove the product element from the DOM
            const productElement = document.querySelector(`[data-product-id="${productId}"]`);
            if (productElement) {
                productElement.remove();
            }
            
            // Update total price
            const totalElement = document.getElementById('total-price');
            if (totalElement) {
                totalElement.textContent = data.total + 'đ';
            }
            
            // If cart is empty, show empty cart message
            if (data.cart_count === 0) {
                const productContainer = document.querySelector('.product-container');
                if (productContainer) {
                    productContainer.innerHTML = '<div class="empty-cart-message"><p>Giỏ hàng của bạn đang trống</p></div>';
                }
            }
        } else {
            console.error('Failed to remove item:', data.message);
        }
    })
    .catch(error => {
        console.error('Error removing item:', error);
    });
}

function clearCart() {
    fetch('/clear-cart', {
        method: 'POST'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            const productContainer = document.querySelector('.product-container');
            if (productContainer) {
                productContainer.innerHTML = '<div class="empty-cart-message"><p>Giỏ hàng của bạn đang trống</p></div>';
            }
            const totalElement = document.getElementById('total-price');
            if (totalElement) {
                totalElement.textContent = '0đ';
            }
        } else {
            console.error('Failed to clear cart:', data.message);
        }
    })
    .catch(error => {
        console.error('Error clearing cart:', error);
    });
} 