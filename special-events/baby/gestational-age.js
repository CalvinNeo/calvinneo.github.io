(function () {
  'use strict';

  var DAY_MS = 24 * 60 * 60 * 1000;
  var STYLE_ID = 'gestational-age-component-styles';
  var instanceCount = 0;

  function pad(number) {
    return String(number).padStart(2, '0');
  }

  // Parse a calendar date without letting the browser interpret it as UTC.
  function parseDate(value) {
    var match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value || '');
    if (!match) {
      return null;
    }

    var date = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
    if (
      date.getFullYear() !== Number(match[1]) ||
      date.getMonth() !== Number(match[2]) - 1 ||
      date.getDate() !== Number(match[3])
    ) {
      return null;
    }

    date.setHours(0, 0, 0, 0);
    return date;
  }

  function padDate(date) {
    return date.getFullYear() + '-' + pad(date.getMonth() + 1) + '-' + pad(date.getDate());
  }

  function utcDay(date) {
    return Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()) / DAY_MS;
  }

  function daysBetween(start, end) {
    return utcDay(end) - utcDay(start);
  }

  function addDays(date, days) {
    var result = new Date(date.getTime());
    result.setDate(result.getDate() + days);
    return result;
  }

  function today() {
    var date = new Date();
    date.setHours(0, 0, 0, 0);
    return date;
  }

  function formatAge(totalDays) {
    if (!Number.isFinite(totalDays)) {
      return '无法计算';
    }

    if (totalDays < 0) {
      return '孕周尚未开始（距参考日 ' + Math.abs(totalDays) + ' 天）';
    }

    return '孕' + Math.floor(totalDays / 7) + '周' + (totalDays % 7) + '天';
  }

  function ensureStyles() {
    if (document.getElementById(STYLE_ID)) {
      return;
    }

    var style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = [
      'gestational-age { display: block; }',
      '.gestational-age-card {',
      '  margin: 1em 0;',
      '  padding: 0.85em 1em;',
      '  border: 1px solid #d8e8e1;',
      '  border-radius: 8px;',
      '  background: #f8fbfa;',
      '  font-size: 0.9em;',
      '}',
      '.gestational-age-card h3 { margin: 0 0 0.6em; font-size: 1.1em; }',
      '.gestational-age-grid {',
      '  display: grid;',
      '  grid-template-columns: repeat(auto-fit, minmax(9em, 1fr));',
      '  gap: 0.5em 0.75em;',
      '  margin: 0.65em 0;',
      '}',
      '.gestational-age-value {',
      '  display: block;',
      '  margin-top: 0.15em;',
      '  color: #2b6954;',
      '  font-size: 1.1em;',
      '  font-weight: 700;',
      '}',
      '.gestational-age-date { color: #65756e; font-size: 0.8em; }',
      '.gestational-age-card label { display: inline-flex; align-items: center; gap: 0.5em; }',
      '.gestational-age-card label { font-size: 0.9em; }',
      '.gestational-age-card input { max-width: 10em; }',
      '.gestational-age-selected { margin: 0.55em 0 0; font-size: 0.9em; }',
      '.gestational-age-error { color: #a33a3a; }'
    ].join('\n');
    document.head.appendChild(style);
  }

  class GestationalAge extends HTMLElement {
    connectedCallback() {
      if (this.initialized) {
        return;
      }
      this.initialized = true;

      this.referenceDate = parseDate(this.getAttribute('reference-date'));
      this.referenceWeeks = Number(this.getAttribute('reference-week'));
      this.referenceDays = Number(this.getAttribute('reference-day'));
      this.referenceAgeDays = this.referenceWeeks * 7 + this.referenceDays;

      if (
        !this.referenceDate ||
        !Number.isInteger(this.referenceWeeks) ||
        !Number.isInteger(this.referenceDays) ||
        this.referenceWeeks < 0 ||
        this.referenceDays < 0 ||
        this.referenceDays > 6
      ) {
        this.innerHTML = '<p class="gestational-age-error">孕周组件配置无效。</p>';
        return;
      }

      ensureStyles();
      this.instanceId = 'gestational-age-' + (++instanceCount);
      this.render();
      this.update();
      this.input.addEventListener('input', this.updateSelected.bind(this));
      this.timer = window.setInterval(this.update.bind(this), 60 * 1000);
    }

    disconnectedCallback() {
      if (this.timer) {
        window.clearInterval(this.timer);
      }
    }

    render() {
      var selectedDate = parseDate(this.getAttribute('selected-date')) || today();
      var dueDate = addDays(this.referenceDate, 280 - this.referenceAgeDays);

      this.innerHTML = [
        '<section class="gestational-age-card" aria-labelledby="', this.instanceId, '-title">',
        '  <h3 id="', this.instanceId, '-title">孕周</h3>',
        '  <div class="gestational-age-grid">',
        '    <div>',
        '      <span>当前时间</span>',
        '      <strong class="gestational-age-value" data-role="current-age"></strong>',
        '      <time class="gestational-age-date" data-role="current-date"></time>',
        '    </div>',
        '    <div>',
        '      <span>预产期</span>',
        '      <strong class="gestational-age-value" data-role="due-date"></strong>',
        '      <time class="gestational-age-date" data-role="due-date-label"></time>',
        '    </div>',
        '  </div>',
        '  <label for="', this.instanceId, '-date">查看指定日期的孕周',
        '    <input id="', this.instanceId, '-date" data-role="selected-date" type="date" value="',
        padDate(selectedDate), '">',
        '  </label>',
        '  <p class="gestational-age-selected" aria-live="polite" data-role="selected-output"></p>',
        '</section>'
      ].join('');

      this.input = this.querySelector('[data-role="selected-date"]');
      this.currentAge = this.querySelector('[data-role="current-age"]');
      this.currentDate = this.querySelector('[data-role="current-date"]');
      this.dueDate = this.querySelector('[data-role="due-date"]');
      this.dueDateLabel = this.querySelector('[data-role="due-date-label"]');
      this.selectedOutput = this.querySelector('[data-role="selected-output"]');
      this.calculatedDueDate = dueDate;
    }

    updateSelected() {
      var selectedDate = parseDate(this.input.value);
      if (!selectedDate) {
        this.selectedOutput.textContent = '请输入有效日期。';
        return;
      }

      this.selectedOutput.textContent = padDate(selectedDate) + '：' +
        formatAge(this.referenceAgeDays + daysBetween(this.referenceDate, selectedDate));
    }

    update() {
      var currentDate = today();
      this.currentAge.textContent = formatAge(
        this.referenceAgeDays + daysBetween(this.referenceDate, currentDate)
      );
      this.currentDate.textContent = padDate(currentDate);
      this.currentDate.dateTime = padDate(currentDate);
      this.dueDate.textContent = padDate(this.calculatedDueDate);
      this.dueDateLabel.textContent = '按 40 周推算';
      this.dueDateLabel.dateTime = padDate(this.calculatedDueDate);
      this.updateSelected();
    }
  }

  if (window.customElements && !window.customElements.get('gestational-age')) {
    window.customElements.define('gestational-age', GestationalAge);
  }
}());
