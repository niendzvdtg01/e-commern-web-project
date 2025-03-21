function openpopup(){
    document.getElementById("loginPopup").style.display="block";
}
function closepopup(){
    document.getElementById("loginPopup").style.display="none";
}
document.addEventListener("DOMContentLoaded", function () {
    let currentIndex = 0;
    const slides = document.querySelectorAll(".slider-img");
    const slider = document.querySelector(".slider");
    const slideWidth = slides[0].offsetWidth + 20; // Lấy kích thước ảnh + khoảng cách

    function updateSlider() {
        slider.style.transform = `translateX(${-currentIndex * slideWidth}px)`;
    }

    document.querySelector(".next").addEventListener("click", function () {
        if (currentIndex < slides.length - 4) {
            currentIndex++;
        } else {
            currentIndex = 0; // Quay lại đầu
        }
        updateSlider();
    });

    document.querySelector(".prev").addEventListener("click", function () {
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            currentIndex = slides.length - 1; // Quay về cuối
        }
        updateSlider();
    });
});
