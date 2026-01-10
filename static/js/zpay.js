document.addEventListener("DOMContentLoaded", () => {
    const msg = document.querySelector(".django-message");
    if (!msg) return;

    const type = msg.dataset.type;
    const text = msg.dataset.text;

    if (type.includes("success")) {
        showToast("success", text);
        showPopup("success", text);
        launchConfetti();
    }

    if (type.includes("error")) {
        showToast("error", text);
        showPopup("error", text);
    }
});

/* TOAST */
function showToast(type, message) {
    const toast = document.getElementById("toast");
    const icon = document.getElementById("toastIcon");
    const text = document.getElementById("toastText");

    toast.className = `toast ${type}`;
    toast.classList.remove("hidden");

    icon.innerHTML = type === "success" ? "✔️" : "❌";
    text.innerText = message;

    setTimeout(() => {
        toast.classList.add("hidden");
    }, 3500);
}

/* POPUP */
function showPopup(type, message) {
    const popup = document.getElementById("paymentPopup");
    const icon = document.getElementById("popupIcon");
    const title = document.getElementById("popupTitle");
    const msg = document.getElementById("popupMessage");

    popup.classList.remove("hidden");

    if (type === "success") {
        icon.innerHTML = "🎉";
        icon.className = "popup-icon success";
        title.innerText = "Payment Successful";
        msg.innerText = message;
    }

    if (type === "error") {
        icon.innerHTML = "❌";
        icon.className = "popup-icon error";
        title.innerText = "Payment Failed";
        msg.innerText = message;
    }
}

function closePopup() {
    document.getElementById("paymentPopup").classList.add("hidden");
}

/* CONFETTI */
function launchConfetti() {
    const canvas = document.getElementById("confettiCanvas");
    const ctx = canvas.getContext("2d");

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const confetti = [];
    const colors = ["#28a745", "#20c997", "#ffc107", "#007bff", "#dc3545"];

    for (let i = 0; i < 150; i++) {
        confetti.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height - canvas.height,
            r: Math.random() * 6 + 4,
            d: Math.random() * 40 + 10,
            color: colors[Math.floor(Math.random() * colors.length)],
            tilt: Math.random() * 10
        });
    }

    let angle = 0;

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        angle += 0.01;

        confetti.forEach((c, i) => {
            ctx.beginPath();
            ctx.fillStyle = c.color;
            ctx.ellipse(c.x, c.y, c.r, c.r * 0.6, c.tilt, 0, Math.PI * 2);
            ctx.fill();

            c.y += Math.cos(angle + c.d) + 3;
            c.x += Math.sin(angle);
        });

        requestAnimationFrame(draw);
    }

    draw();

    setTimeout(() => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }, 3000);
}
