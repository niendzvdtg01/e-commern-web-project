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
    if (!productId) {
        console.error('Product ID is required');
        return;
    }

    // Get the product element
    const productElement = document.querySelector(`[data-product-id="${productId}"]`);
    if (!productElement) {
        console.error('Product element not found');
        return;
    }

    // Create form data
    const formData = new FormData();
    formData.append('product_id', productId);

    // Send request to remove item
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
            if (productElement) {
                productElement.remove();
            }
            
            // Update total price
            const totalElement = document.getElementById('total-price');
            if (totalElement) {
                totalElement.textContent = data.total.toLocaleString('vi-VN') + 'đ';
            }
            
            // If cart is empty, show empty cart message
            const productContainer = document.querySelector('.product-container');
            if (productContainer) {
                const remainingProducts = productContainer.querySelectorAll('.bbbbbb');
                if (remainingProducts.length === 0) {
                    productContainer.innerHTML = '<div class="empty-cart-message"><p>Giỏ hàng của bạn đang trống</p></div>';
                }
            }
            
            // Update cart count in header if it exists
            const cartCount = document.getElementById('cart-count');
            if (cartCount) {
                cartCount.textContent = data.cart_count;
            }
        } else {
            console.error('Failed to remove item:', data.message);
            alert(data.message || 'Failed to remove item from cart');
        }
    })
    .catch(error => {
        console.error('Error removing item:', error);
        alert('An error occurred while removing the item');
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

// Function to handle adding items to cart from product list
function addToCart(productId) {
    const form = document.getElementById(`add-to-cart-form-${productId}`);
    const formData = new FormData(form);
    
    fetch('/add-to-cart', {
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
        const messageDiv = document.getElementById(`cart-message-${productId}`);
        if (data.success) {
            messageDiv.textContent = data.message;
            messageDiv.style.display = 'block';
            messageDiv.style.color = 'green';
            
            // Update cart count in header if it exists
            const cartCount = document.getElementById('cart-count');
            if (cartCount) {
                cartCount.textContent = data.cart_count;
            }
        } else {
            messageDiv.textContent = data.message;
            messageDiv.style.display = 'block';
            messageDiv.style.color = 'red';
        }
        
        // Hide message after 3 seconds
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 3000);
    })
    .catch(error => {
        console.error('Error adding to cart:', error);
        const messageDiv = document.getElementById(`cart-message-${productId}`);
        messageDiv.textContent = 'Có lỗi xảy ra, vui lòng thử lại';
        messageDiv.style.display = 'block';
        messageDiv.style.color = 'red';
        
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 3000);
    });
} 