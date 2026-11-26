/* Mythoria — демонстрация прозрачного персонажа и игровых эффектов. */
(() => {
  'use strict';
  const scene = document.querySelector('[data-hero-stage]');
  if (!scene) return;

  const shell = document.querySelector('[data-demo-shell]');
  const worldButtons = [...shell.querySelectorAll('[data-demo-world]')];
  const abilityButtons = [...shell.querySelectorAll('[data-demo-ability]')];
  const layers = [...scene.querySelectorAll('[data-background-layer]')];
  const status = scene.querySelector('[data-demo-status]');
  const subtitle = scene.querySelector('[data-demo-subtitle]');
  const summon = scene.querySelector('[data-summon]');
  const motion = shell.querySelector('[data-demo-motion]');
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let motionEnabled = !prefersReduced.matches;
  let currentBackground = 0;
  let sceneTimer = 0;
  let frame = 0;
  let position = {x: 0, y: 0};

  function setMotion(enabled) {
    motionEnabled = enabled && !prefersReduced.matches;
    scene.classList.toggle('demo-motion-off', !motionEnabled);
    motion.setAttribute('aria-pressed', String(motionEnabled));
    motion.innerHTML = `<span class="demo-motion-indicator"></span>${motionEnabled ? 'Анимация включена' : 'Анимация выключена'}`;
    scene.style.setProperty('--parallax-x', '0px');
    scene.style.setProperty('--parallax-y', '0px');
    scene.style.setProperty('--tilt-x', '0deg');
    scene.style.setProperty('--tilt-y', '0deg');
    scene.style.setProperty('--card-tilt-x', '0deg');
    scene.style.setProperty('--card-tilt-y', '0deg');
  }
  setMotion(motionEnabled);
  motion.addEventListener('click', () => setMotion(!motionEnabled));
  prefersReduced.addEventListener?.('change', () => setMotion(!prefersReduced.matches));

  worldButtons.forEach(button => button.addEventListener('click', () => {
    if (button.classList.contains('is-selected')) return;
    const target = 1 - currentBackground;
    const url = button.dataset.worldImage;
    if (!url) return;
    // Preload to avoid a blank flash during transition.
    const picture = new Image();
    picture.onload = () => {
      layers[target].style.backgroundImage = `linear-gradient(90deg,rgba(4,10,29,.94) 0%,rgba(6,14,35,.75) 34%,rgba(5,12,33,.32) 75%),url("${url}")`;
      layers[target].classList.add('demo-bg-active');
      layers[currentBackground].classList.remove('demo-bg-active');
      currentBackground = target;
      scene.dataset.world = button.dataset.demoWorld;
      worldButtons.forEach(b => {
        const active = b === button;
        b.classList.toggle('is-selected', active);
        b.setAttribute('aria-pressed', String(active));
      });
      status.textContent = button.dataset.worldName;
      subtitle.textContent = 'Мир изменён — персонаж остаётся прежним';
    };
    picture.onerror = () => {
      status.textContent = 'Фон пока не загрузился';
      subtitle.textContent = 'Попробуйте выбрать другой мир';
    };
    picture.src = url;
  }));

  const labels = {
    sword: ['Клинок пробудился', 'Энергия пробегает вдоль меча'],
    shield: ['Щит под защитой', 'Магическая аура укрепляет оборону'],
    arcane: ['Магическая аура активна', 'Руны и портал сияют ярче']
  };
  abilityButtons.forEach(button => button.addEventListener('click', () => {
    const type = button.dataset.demoAbility;
    const active = button.getAttribute('aria-pressed') !== 'true';
    button.setAttribute('aria-pressed', String(active));
    scene.classList.toggle(`is-${type}`, active);
    status.textContent = active ? labels[type][0] : 'Эффект отключён';
    subtitle.textContent = active ? labels[type][1] : 'Выберите другую способность';
  }));

  summon.addEventListener('click', () => {
    if (summon.disabled) return;
    if (!motionEnabled) {
      status.textContent = 'Страж рассвета призван';
      subtitle.textContent = 'Режим без движения';
      return;
    }
    window.clearTimeout(sceneTimer);
    scene.classList.remove('is-summoning');
    void scene.offsetWidth; // Перезапускаем CSS-анимацию при повторном нажатии.
    scene.classList.add('is-summoning');
    summon.disabled = true;
    status.textContent = 'Магический призыв';
    subtitle.textContent = 'Герой появляется сквозь портал';
    sceneTimer = window.setTimeout(() => {
      scene.classList.remove('is-summoning');
      summon.disabled = false;
      status.textContent = 'Страж рассвета призван';
      subtitle.textContent = 'Теперь попробуйте эффекты меча и щита';
    }, 1800);
  });

  // Cursor movement is limited to fine pointers; no gyroscope or tracking is used.
  const finePointer = window.matchMedia('(pointer:fine)');
  scene.addEventListener('pointermove', event => {
    if (!motionEnabled || !finePointer.matches || scene.classList.contains('is-summoning')) return;
    const rect = scene.getBoundingClientRect();
    position = {
      x: Math.max(-1, Math.min(1, ((event.clientX - rect.left) / rect.width - .5) * 2)),
      y: Math.max(-1, Math.min(1, ((event.clientY - rect.top) / rect.height - .5) * 2))
    };
    if (frame) return;
    frame = window.requestAnimationFrame(() => {
      scene.style.setProperty('--parallax-x', `${(position.x * 19).toFixed(2)}px`);
      scene.style.setProperty('--parallax-y', `${(position.y * 12).toFixed(2)}px`);
      scene.style.setProperty('--tilt-x', `${(position.x * -2.2).toFixed(2)}deg`);
      scene.style.setProperty('--tilt-y', `${(position.y * 1.4).toFixed(2)}deg`);
      scene.style.setProperty('--card-tilt-x', `${(position.x * -.85).toFixed(2)}deg`);
      scene.style.setProperty('--card-tilt-y', `${(position.y * .65).toFixed(2)}deg`);
      frame = 0;
    });
  }, {passive: true});
  scene.addEventListener('pointerleave', () => {
    if (frame) window.cancelAnimationFrame(frame);
    frame = 0;
    for (const [name, value] of [['--parallax-x','0px'], ['--parallax-y','0px'], ['--tilt-x','0deg'], ['--tilt-y','0deg'], ['--card-tilt-x','0deg'], ['--card-tilt-y','0deg']]) scene.style.setProperty(name, value);
  });
})();
