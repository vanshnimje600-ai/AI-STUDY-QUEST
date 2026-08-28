let timeLeft = 15;

const timer = document.getElementById("timer");

const countdown = setInterval(function () {

    timer.innerHTML = "⏱ " + timeLeft + " sec";

    timeLeft--;

    if (timeLeft < 0) {

        clearInterval(countdown);

        alert("Time's Up!");

        document.getElementById("quizForm").submit();

    }

}, 1000);