document.addEventListener('DOMContentLoaded', function () {
    const mainImage = document.getElementById('main-image');
    const thumbnails = document.querySelectorAll('.thumbnail');

    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function () {
            // Xóa lớp active khỏi tất cả các thumbnail
            thumbnails.forEach(thumb => thumb.classList.remove('active'));
            // Thêm lớp active cho thumbnail được chọn
            this.classList.add('active');
            // Lấy đường dẫn ảnh lớn từ thuộc tính data-src
            const newSrc = this.getAttribute('data-src');
            // Thay đổi src của ảnh chính
            mainImage.setAttribute('src', newSrc);
        });
    });

    // Đặt ảnh đầu tiên làm mặc định có lớp active
    if (thumbnails.length > 0) {
        thumbnails[0].classList.add('active');
    }
});
