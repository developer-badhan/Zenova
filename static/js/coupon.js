// Coupone Message 

document.querySelectorAll(".coupon-form").forEach(form => {
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const url = this.action;
    const csrf = this.querySelector("[name=csrfmiddlewaretoken]").value;
    const couponId = this.dataset.couponId;
    const button = this.querySelector(".apply-btn");

    fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrf,
      },
    })
    .then(res => res.text())
    .then(html => {
      document.getElementById("coupon-message").innerHTML = html;

      // success → update UI
      if (html.includes("alert-success")) {
        const countEl = document.querySelector(
          `.used-count[data-coupon-id="${couponId}"]`
        );

        let current = parseInt(countEl.innerText);
        countEl.innerText = current + 1;

        button.disabled = true;
        button.classList.remove("btn-primary");
        button.classList.add("btn-secondary");
        button.innerText = "Used";
      }
    });
  });
});
