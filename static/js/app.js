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
