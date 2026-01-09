function showComingSoon(method) {
    const paymentName = document.getElementById('paymentName');
    const popupLogo = document.getElementById('popupLogo');

    paymentName.innerText = method;
    paymentName.className = '';

    if (method === 'Google Pay') {
        paymentName.classList.add('google-pay-text');
        popupLogo.src = "/static/images/gpay.png";
        popupLogo.alt = "Google Pay";
        popupLogo.style.display = 'block';
    } 
    else if (method === 'PhonePe') {
        paymentName.classList.add('phonepe-text');
        popupLogo.src = "/static/images/phonepe.png";
        popupLogo.alt = "PhonePe";
        popupLogo.style.display = 'block';
    }

    document.getElementById('comingSoonModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('comingSoonModal').style.display = 'none';
}
