(() => {
  const navToggle = document.querySelector('[data-nav-toggle]');
  const nav = document.querySelector('[data-site-nav]');
  navToggle?.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', String(open));
  });

  const progress = document.querySelector('[data-progress]');
  if (progress) {
    const update = () => {
      const max = document.documentElement.scrollHeight - innerHeight;
      progress.style.width = `${max > 0 ? (scrollY / max) * 100 : 0}%`;
    };
    addEventListener('scroll', update, { passive: true });
    update();
  }

  const article = document.querySelector('.article-body');
  const tocList = document.querySelector('[data-toc]');
  if (article && tocList) {
    const headings = [...article.querySelectorAll('h2[id], h3[id]')];
    headings.forEach((heading) => {
      const li = document.createElement('li');
      if (heading.tagName === 'H3') li.className = 'depth-3';
      const link = document.createElement('a');
      link.href = `#${heading.id}`;
      link.textContent = heading.textContent;
      li.append(link);
      tocList.append(li);
    });

    const links = [...tocList.querySelectorAll('a')];
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).at(-1);
      if (!visible) return;
      links.forEach((link) => link.classList.toggle('active', link.hash === `#${visible.target.id}`));
    }, { rootMargin: '-20% 0px -68% 0px', threshold: 0 });
    headings.forEach((heading) => observer.observe(heading));
  }

  document.querySelector('[data-copy-link]')?.addEventListener('click', async (event) => {
    try {
      await navigator.clipboard.writeText(location.href);
      event.currentTarget.textContent = 'Ссылка скопирована';
      setTimeout(() => { event.currentTarget.textContent = 'Скопировать ссылку'; }, 1800);
    } catch {
      event.currentTarget.textContent = 'Не удалось скопировать';
    }
  });
})();

