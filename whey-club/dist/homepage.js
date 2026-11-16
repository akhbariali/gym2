(() => {
  const video = document.querySelector('#trainingVideo');
  if (!video) return;
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  if (!motion.matches && !navigator.connection?.saveData) {
    // Autoplay can be blocked; native controls and the poster remain available.
    video.play().catch(() => {});
  }
  motion.addEventListener('change', event => { if (event.matches) video.pause(); });
})();
