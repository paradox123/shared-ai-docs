// Tab selection changes visibility only; observation keeps its nodes and focus.
export function runTabs(container, initial, onSelect) {
  const tabs = [...container.querySelectorAll('[role="tab"]')];
  function select(tab) {
    for (const item of tabs) {
      const selected = item === tab;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
      document.getElementById(item.getAttribute('aria-controls')).hidden = !selected;
    }
    onSelect(tab.dataset.view);
  }
  for (const tab of tabs) {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', event => {
      let index = tabs.indexOf(tab);
      if (event.key === 'ArrowRight') index = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') index = (index + tabs.length - 1) % tabs.length;
      else if (event.key === 'Home') index = 0;
      else if (event.key === 'End') index = tabs.length - 1;
      else return;
      event.preventDefault();
      select(tabs[index]);
      tabs[index].focus();
    });
  }
  select(tabs.find(tab => tab.dataset.view === initial) || tabs[0]);
}
