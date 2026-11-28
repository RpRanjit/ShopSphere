
document.addEventListener("DOMContentLoaded", function () {

    const slides = document.querySelectorAll(".slide");
    const track = document.querySelector(".slides-track");

    // Create a duplicate of the first slide
    const firstClone = slides[0].cloneNode(true);
    track.appendChild(firstClone);
    const prevButton = document.querySelector(".slider-arrow.prev");
    const nextButton = document.querySelector(".slider-arrow.next");
    const dots = document.querySelectorAll(".dot");

    let currentIndex = 0;
    let slideInterval;

    // Display a particular slide

function showSlide(index) {

    dots.forEach(dot => {
        dot.classList.remove("active");
    });

    dots[index % slides.length].classList.add("active");

    track.style.transform = `translateX(-${index * 100}%)`;

    currentIndex = index;
}

track.addEventListener("transitionend", function () {

    if (currentIndex === slides.length) {

        track.style.transition = "none";
        track.style.transform = "translateX(0%)";

        currentIndex = 0;

        // Restore the animation
        track.offsetHeight;
        track.style.transition = "";
    }

});

    // Move to the next slide
    function nextSlide() {
    showSlide(currentIndex + 1);
}

    // Move to the previous slide
    function previousSlide() {
        let previousIndex =
            (currentIndex - 1 + slides.length) % slides.length;

        showSlide(previousIndex);
    }

    // Start automatic sliding
    function startAutoSlide() {
        slideInterval = setInterval(nextSlide, 3000);
    }

    // Reset automatic sliding after manual interaction
    function resetAutoSlide() {
        clearInterval(slideInterval);
        startAutoSlide();
    }

    // Next arrow
    nextButton.addEventListener("click", function () {
        nextSlide();
        resetAutoSlide();
    });

    // Previous arrow
    prevButton.addEventListener("click", function () {
        previousSlide();
        resetAutoSlide();
    });

    // Indicator dots
    dots.forEach((dot, index) => {
        dot.addEventListener("click", function () {
            showSlide(index);
            resetAutoSlide();
        });
    });

    // Start the slider
    startAutoSlide();

});
