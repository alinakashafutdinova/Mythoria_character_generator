'use strict';

// Меню на телефоне
const menu = document.querySelector('.mobile-nav-toggle');
const nav = document.querySelector('.main-nav');
if (menu && nav) {
  menu.addEventListener('click', () => {
    const expanded = menu.getAttribute('aria-expanded') === 'true';
    menu.setAttribute('aria-expanded', String(!expanded));
    menu.setAttribute('aria-label', expanded ? 'Открыть меню' : 'Закрыть меню');
    nav.classList.toggle('open', !expanded);
  });
  nav.addEventListener('click', event => {
    if (event.target.closest('a')) {
      menu.setAttribute('aria-expanded', 'false');
      menu.setAttribute('aria-label', 'Открыть меню');
      nav.classList.remove('open');
    }
  });
}

// Подтверждение удаления сохранённых персонажей
for (const form of document.querySelectorAll('form[data-confirm]')) {
  form.addEventListener('submit', event => {
    if (!window.confirm(form.dataset.confirm)) event.preventDefault();
  });
}

// Фильтр каталога игр
const filterTabs = document.querySelectorAll('.tab[data-filter]');
const gameCards = document.querySelectorAll('.game-card[data-group]');
for (const tab of filterTabs) {
  tab.addEventListener('click', () => {
    for (const t of filterTabs) {
      t.classList.toggle('active', t === tab);
      t.setAttribute('aria-pressed', String(t === tab));
    }
    for (const card of gameCards) {
      card.hidden = tab.dataset.filter !== 'all' && card.dataset.group !== tab.dataset.filter;
    }
  });
}

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Плавное появление блоков при прокрутке, без скрытия контента при отсутствии JS
if (!reduceMotion && 'IntersectionObserver' in window) {
  document.body.classList.add('js-motion');
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    }
  }, { threshold: 0.09, rootMargin: '0px 0px 40px 0px' });
  for (const block of document.querySelectorAll('.my-reveal')) observer.observe(block);
}

// Плавающие световые частицы на первом экране
const stars = document.querySelector('[data-stardust]');
if (stars && !reduceMotion) {
  for (let i = 0; i < 24; i++) {
    const star = document.createElement('span');
    star.className = 'my-star';
    star.style.left = `${(i * 37 + 15) % 100}%`;
    star.style.top = `${(i * 59 + 22) % 92}%`;
    star.style.animationDelay = `${((i * 7) % 30) / -4}s`;
    star.style.animationDuration = `${6 + (i % 5)}s`;
    stars.append(star);
  }
}

// Карусель каталога: кнопки, точки, автоматическое перелистывание и пауза при наведении
for (const carousel of document.querySelectorAll('[data-carousel]')) {
  const track = carousel.querySelector('[data-carousel-track]');
  const dots = carousel.querySelector('[data-carousel-dots]');
  if (!track) continue;
  let page = 0;
  let pages = 1;
  let paused = false;
  let autoplay;

  const pageWidth = () => Math.max(1, track.clientWidth - 2);
  const updateDots = () => {
    if (!dots) return;
    pages = Math.max(1, Math.ceil(track.scrollWidth / pageWidth()));
    page = Math.min(page, pages - 1);
    dots.replaceChildren();
    for (let index = 0; index < pages; index++) {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'my-carousel-dot';
      dot.setAttribute('aria-label', `Страница ${index + 1} из ${pages}`);
      dot.addEventListener('click', () => moveTo(index));
      dots.append(dot);
    }
    highlightDots();
  };
  const highlightDots = () => {
    for (const [index, dot] of [...(dots?.children || [])].entries()) {
      dot.classList.toggle('is-active', index === page);
      dot.setAttribute('aria-current', index === page ? 'true' : 'false');
    }
  };
  const moveTo = index => {
    page = (index + pages) % pages;
    track.scrollTo({left: page * pageWidth(), behavior: reduceMotion ? 'auto' : 'smooth'});
    highlightDots();
  };
  carousel.querySelector('[data-carousel-prev]')?.addEventListener('click', () => moveTo(page - 1));
  carousel.querySelector('[data-carousel-next]')?.addEventListener('click', () => moveTo(page + 1));
  track.addEventListener('scroll', () => {
    page = Math.min(pages - 1, Math.max(0, Math.round(track.scrollLeft / pageWidth())));
    highlightDots();
  }, {passive: true});
  carousel.addEventListener('mouseenter', () => paused = true);
  carousel.addEventListener('mouseleave', () => paused = false);
  carousel.addEventListener('focusin', () => paused = true);
  carousel.addEventListener('focusout', () => paused = false);
  updateDots();
  window.addEventListener('resize', updateDots, {passive:true});
  if (!reduceMotion && Number(carousel.dataset.autoplay) >= 3000) {
    autoplay = window.setInterval(() => {
      if (!paused && !document.hidden && pages > 1 && carousel.getBoundingClientRect().bottom > 0) {
        moveTo(page + 1);
      }
    }, Number(carousel.dataset.autoplay));
  }
}

// Примеры героев: декоративная галерея. Основной генератор работает отдельно.
const showcase = document.querySelector('[data-showcase]');
if (showcase) {
  const heroes = [
    {name:'КАЙДРЕН', role:'Воин · Защитник', game:'dnd',
     story:'Страж пограничных земель. Он защищает слабых и умеет обращать древнюю магию себе на помощь.',
     stats:[['Сила',82],['Ловкость',68],['Магия',71]]},
    {name:'АРИЭЛЬ',role:'Волшебница · Исследовательница',game:'bg3',
     story:'Хранительница звёздных путей, которая ищет источник света между мирами.',
     stats:[['Сила',43],['Интеллект',94],['Магия',98]]},
    {name:'ОДЕТТА',role:'Заклинательница · Поддержка',game:'divinity',
     story:'Повелевает стихиями и умеет направлять энергию союзников в самый сложный момент.',
     stats:[['Ловкость',70],['Интеллект',91],['Магия',96]]},
    {name:'ЛИРА',role:'Следопыт · Путешественница',game:'pathfinder',
     story:'Путешествует по забытым лесам, собирая истории древних королевств.',
     stats:[['Сила',61],['Ловкость',90],['Мудрость',84]]}
  ];
  const cards = [...showcase.querySelectorAll('[data-hero-index]')];
  const dots = showcase.querySelector('[data-showcase-dots]');
  let active = 0;
  const update = index => {
    active = (index + cards.length) % cards.length;
    const hero = heroes[active];
    showcase.querySelector('[data-hero-name]').textContent = hero.name;
    showcase.querySelector('[data-hero-role]').textContent = hero.role;
    showcase.querySelector('[data-hero-story]').textContent = hero.story;
    showcase.querySelector('[data-hero-link]').href = `/generate/${encodeURIComponent(hero.game)}`;
    const stats = showcase.querySelector('[data-hero-stats]');
    stats.replaceChildren();
    for (const [name, value] of hero.stats) {
      const row = document.createElement('div');
      row.className = 'my-ability';
      const label = document.createElement('span');
      label.textContent = name;
      const bar = document.createElement('div');
      const fill = document.createElement('i');
      fill.style.width = `${value}%`;
      bar.append(fill);
      const num = document.createElement('b');
      num.textContent = String(value);
      row.append(label, bar, num);
      stats.append(row);
    }
    for (let i = 0; i < cards.length; i++) {
      const distance = (i - active + cards.length) % cards.length;
      cards[i].classList.toggle('is-active', distance === 0);
      cards[i].classList.toggle('is-right', distance === 1);
      cards[i].classList.toggle('is-left', distance === cards.length - 1);
      cards[i].classList.toggle('is-hidden', distance !== 0 && distance !== 1 && distance !== cards.length - 1);
      cards[i].setAttribute('aria-pressed', String(distance === 0));
      cards[i].tabIndex = distance === 0 || distance === 1 || distance === cards.length - 1 ? 0 : -1;
    }
    for (const [i, dot] of [...dots.children].entries()) {
      dot.classList.toggle('is-active', i === active);
      dot.setAttribute('aria-current', i === active ? 'true' : 'false');
    }
  };
  for (let i = 0; i < cards.length; i++) {
    const dot = document.createElement('button');
    dot.className = 'my-carousel-dot';
    dot.type = 'button';
    dot.setAttribute('aria-label', `Показать персонажа ${heroes[i].name}`);
    dot.addEventListener('click', () => update(i));
    dots.append(dot);
    cards[i].addEventListener('click', () => update(i));
  }
  showcase.querySelector('[data-showcase-prev]')?.addEventListener('click', () => update(active - 1));
  showcase.querySelector('[data-showcase-next]')?.addEventListener('click', () => update(active + 1));
  showcase.addEventListener('keydown', event => {
    if (!event.target.closest('[data-coverflow]')) return;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      update(active + (event.key === 'ArrowRight' ? 1 : -1));
      cards[active].focus();
    }
  });
  update(0);
}

// Небольшой наклон промо-карточки на устройствах с мышью
if (!reduceMotion && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
  for (const el of document.querySelectorAll('[data-tilt]')) {
    el.addEventListener('pointermove', event => {
      const rect = el.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - .5;
      const y = (event.clientY - rect.top) / rect.height - .5;
      el.style.transform = `perspective(1000px) rotateY(${x * 2}deg) rotateX(${-y * 2}deg)`;
    });
    el.addEventListener('pointerleave', () => el.style.transform = '');
  }
}

// Внутренние страницы: поиск по игровым мирам и подсчёт найденных карточек.
const gameSearch = document.querySelector('[data-game-search]');
if (gameSearch) {
  const cards = [...document.querySelectorAll('.in-game-card[data-game-title]')];
  const tabs = [...document.querySelectorAll('.in-tabs [data-filter]')];
  const count = document.querySelector('[data-visible-count]');
  const empty = document.querySelector('[data-game-empty]');
  const updateCards = () => {
    const query = gameSearch.value.trim().toLocaleLowerCase('ru');
    const selected = tabs.find(tab => tab.classList.contains('active'))?.dataset.filter || 'all';
    let visible = 0;
    for (const card of cards) {
      const fitsName = card.dataset.gameTitle.toLocaleLowerCase('ru').includes(query);
      const fitsType = selected === 'all' || selected === card.dataset.group;
      card.hidden = !(fitsName && fitsType);
      if (!card.hidden) visible++;
    }
    if (count) count.textContent = `Найдено игр: ${visible}`;
    if (empty) empty.hidden = visible !== 0;
  };
  gameSearch.addEventListener('input', updateCards);
  for (const tab of tabs) tab.addEventListener('click', updateCards);
  updateCards();
}

// Два способа задать уровень: поле и ползунок должны совпадать.
const levelField = document.querySelector('#level');
const levelRange = document.querySelector('#level-range');
if (levelField && levelRange) {
  levelRange.addEventListener('input', () => { levelField.value = levelRange.value; });
  levelField.addEventListener('input', () => {
    const level = Number(levelField.value);
    if (Number.isFinite(level) && level >= Number(levelField.min) && level <= Number(levelField.max)) {
      levelRange.value = String(level);
    }
  });
}

// Кнопка выбора случайной комбинации в форме генератора.
const randomSetup = document.querySelector('[data-random-setup]');
if (randomSetup) {
  randomSetup.addEventListener('click', () => {
    for (const select of document.querySelectorAll('#generation-form select')) {
      const values = [...select.options].filter(option => option.value);
      if (values.length) select.value = values[Math.floor(Math.random() * values.length)].value;
    }
    const level = document.querySelector('#level');
    if (level && levelRange) {
      level.value = String(1 + Math.floor(Math.random() * Math.min(Number(level.max), 20)));
      levelRange.value = level.value;
    }
    randomSetup.animate?.([
      {transform: 'scale(1)'}, {transform: 'scale(.97)'}, {transform: 'scale(1)'}
    ], {duration: 280, easing: 'ease-out'});
  });
}

// Полосы характеристик отображают действительные значения БД/генератора.
if (!reduceMotion && 'IntersectionObserver' in window) {
  const statObserver = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-ready');
        statObserver.unobserve(entry.target);
      }
    }
  }, {threshold: .16});
  for (const bar of document.querySelectorAll('.in-stat-fill')) statObserver.observe(bar);
}

// Mythoria v4: мягкое свечение следует за указателем на игровых карточках.
if (!reduceMotion && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
  const glowCards = document.querySelectorAll('.my-world-card,.in-game-card,.in-hero-card,.my-feature');
  for (const card of glowCards) {
    card.addEventListener('pointermove', event => {
      const bounds = card.getBoundingClientRect();
      card.style.setProperty('--v4-pointer-x', `${(event.clientX - bounds.left).toFixed(1)}px`);
      card.style.setProperty('--v4-pointer-y', `${(event.clientY - bounds.top).toFixed(1)}px`);
    }, {passive:true});
  }
}

// Магический призыв героя: POST остаётся рабочим и без JavaScript.
// В режиме JS получаем готовый HTML с Flask и обновляем только карточку результата.
const generationForm = document.querySelector('#generation-form');
if (generationForm) {
  const resultElement = () => document.querySelector('#generation-result');
  let summoning = false;
  const makePortal = () => {
    const portal = document.createElement('div');
    portal.className = 'v4-portal-overlay';
    portal.setAttribute('role','status');
    portal.setAttribute('aria-live','polite');
    portal.innerHTML = `<div class="v4-portal-core"><span class="v4-portal-icon" aria-hidden="true">✧</span><span class="v4-portal-caption">СОЗДАЁМ ВАШЕГО ГЕРОЯ…</span></div>`;
    if (!reduceMotion) {
      const core = portal.querySelector('.v4-portal-core');
      for (let i = 0; i < 30; i++) {
        const p = document.createElement('i');
        p.className = 'v4-portal-particle';
        p.style.setProperty('--angle', `${i * 12}deg`);
        p.style.setProperty('--radius', `${76 + (i % 5) * 23}px`);
        p.style.setProperty('--speed', `${1.8 + (i % 4) * .3}s`);
        p.style.setProperty('--delay', `${(i % 7) * -.2}s`);
        core.append(p);
      }
    }
    document.body.append(portal);
    return portal;
  };
  generationForm.addEventListener('submit', async event => {
    if (summoning || !generationForm.reportValidity()) return;
    event.preventDefault();
    summoning = true;
    const button = generationForm.querySelector('[type="submit"]');
    if (button) button.disabled = true;
    const portal = makePortal();
    const started = performance.now();
    try {
      const response = await fetch(generationForm.action, {
        method:'POST', body:new FormData(generationForm), credentials:'same-origin',
        headers:{'X-Requested-With':'XMLHttpRequest'}
      });
      if (!response.ok) throw new Error(`Ответ сервера: ${response.status}`);
      const documentCopy = new DOMParser().parseFromString(await response.text(),'text/html');
      const next = documentCopy.querySelector('#generation-result');
      if (!next || !next.querySelector('.in-result-main')) {
        const notice = documentCopy.querySelector('.notice');
        throw new Error(notice?.textContent?.trim() || 'Генератор не вернул персонажа.');
      }
      if (!reduceMotion) await new Promise(resolve => setTimeout(resolve,Math.max(0,950-(performance.now()-started))));
      resultElement()?.replaceWith(next);
      for (const bar of next.querySelectorAll('.in-stat-fill')) bar.classList.add('is-ready');
      if (window.innerWidth < 850) next.scrollIntoView({behavior:reduceMotion?'auto':'smooth',block:'start'});
    } catch (error) {
      // На сетевых ошибках показываем причину, не удаляя пользовательские настройки.
      const notice = document.createElement('div');
      notice.className = 'notice error';
      notice.setAttribute('role','alert');
      notice.textContent = `Не удалось создать героя: ${error.message}. Попробуйте снова.`;
      generationForm.before(notice);
      window.setTimeout(() => notice.remove(),9000);
    } finally {
      portal.classList.add('is-finished');
      window.setTimeout(() => portal.remove(),reduceMotion?0:360);
      if (button) button.disabled = false;
      summoning = false;
    }
  });
}
