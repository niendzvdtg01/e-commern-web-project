function openpopup(){
    document.getElementById("loginPopup").style.display="block";
}
function closepopup(){
    document.getElementById("loginPopup").style.display="none";
}

function opensearch() {
    let popup = document.getElementById("search-popup");
    if (popup) {
        popup.style.display = "block";
        setTimeout(() => {
            popup.classList.add("active");
        }, 10);
    } else {
        console.error("Không tìm thấy phần tử có ID 'search-popup'");
    }
}

function closesearch() {
    let popup = document.getElementById("search-popup");
    popup.classList.remove("active");
    setTimeout(() => {
        popup.style.display = "none"; // Ẩn sau khi hiệu ứng kết thúc
    }, 300); // Đợi transition hoàn thành (0.3s)
}

