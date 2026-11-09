// Aetheris — interactive lessons with local progress.
(function () {
  "use strict";

  var dataEl = document.getElementById("lessons-data");
  if (!dataEl) return;

  var lessons = [];
  try {
    lessons = JSON.parse(dataEl.textContent) || [];
  } catch (err) {
    lessons = [];
  }
  if (!lessons.length) return;

  var STORAGE_KEY = "aetheris.lessons.v1";
  var PASS_RATIO = 0.67;

  var els = {
    list: document.getElementById("lesson-list"),
    title: document.getElementById("lesson-title"),
    desc: document.getElementById("lesson-desc"),
    badge: document.getElementById("lesson-badge"),
    content: document.getElementById("lesson-content"),
    form: document.getElementById("quiz-form"),
    status: document.getElementById("quiz-status"),
    best: document.getElementById("best-score"),
    progressText: document.getElementById("progress-text"),
    progressBar: document.getElementById("progress-bar"),
    scoreText: document.getElementById("score-text"),
    submit: document.getElementById("submit-quiz-btn"),
    next: document.getElementById("next-lesson-btn"),
    reset: document.getElementById("reset-progress-btn"),
  };

  var state = loadState();
  var activeId = state.lastLesson && byId(state.lastLesson) ? state.lastLesson : lessons[0].id;

  function loadState() {
    var fallback = { scores: {}, lastLesson: null };
    try {
      var raw = window.localStorage.getItem(STORAGE_KEY);
      if (!raw) return fallback;
      var parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== "object") return fallback;
      return {
        scores: parsed.scores && typeof parsed.scores === "object" ? parsed.scores : {},
        lastLesson: typeof parsed.lastLesson === "string" ? parsed.lastLesson : null,
      };
    } catch (err) {
      return fallback;
    }
  }

  function saveState() {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (err) {
      /* storage may be unavailable */
    }
  }

  function byId(id) {
    return lessons.filter(function (lesson) {
      return lesson.id === id;
    })[0];
  }

  function lessonIndex(id) {
    return lessons.findIndex(function (lesson) {
      return lesson.id === id;
    });
  }

  function bestScore(lesson) {
    var stored = state.scores[lesson.id];
    return typeof stored === "number" ? stored : 0;
  }

  function isComplete(lesson) {
    var total = lesson.quiz.length;
    return total > 0 && bestScore(lesson) / total >= PASS_RATIO;
  }

  function completedCount() {
    return lessons.filter(isComplete).length;
  }

  function totalScore() {
    return lessons.reduce(function (sum, lesson) {
      return sum + bestScore(lesson);
    }, 0);
  }

  function renderList() {
    els.list.innerHTML = "";
    lessons.forEach(function (lesson, index) {
      var button = document.createElement("button");
      button.type = "button";
      button.className = "lesson-item" + (lesson.id === activeId ? " is-active" : "");
      button.dataset.lessonId = lesson.id;

      var num = document.createElement("span");
      num.className = "lesson-item-num";
      num.textContent = isComplete(lesson) ? "✓" : String(index + 1);
      if (isComplete(lesson)) num.classList.add("is-done");

      var body = document.createElement("span");
      body.className = "lesson-item-body";

      var name = document.createElement("span");
      name.className = "lesson-item-title";
      name.textContent = lesson.title;

      var meta = document.createElement("span");
      meta.className = "lesson-item-meta";
      meta.textContent = bestScore(lesson) + "/" + lesson.quiz.length + " best";

      body.appendChild(name);
      body.appendChild(meta);
      button.appendChild(num);
      button.appendChild(body);
      button.addEventListener("click", function () {
        activeId = lesson.id;
        state.lastLesson = activeId;
        saveState();
        render();
      });
      els.list.appendChild(button);
    });
  }

  function renderLesson() {
    var lesson = byId(activeId) || lessons[0];
    els.title.textContent = lesson.title;
    els.desc.textContent = lesson.desc;
    els.badge.textContent = lesson.badge || "Lesson";

    els.content.innerHTML = "";
    lesson.content.forEach(function (item) {
      var li = document.createElement("li");
      li.innerHTML = item;
      els.content.appendChild(li);
    });
  }

  function renderQuiz() {
    var lesson = byId(activeId) || lessons[0];
    els.form.innerHTML = "";

    lesson.quiz.forEach(function (question, qIndex) {
      var fieldset = document.createElement("fieldset");
      fieldset.className = "quiz-question";

      var legend = document.createElement("legend");
      legend.innerHTML = "<span class=\"quiz-num\">" + (qIndex + 1) + "</span>" + question.q;
      fieldset.appendChild(legend);

      var group = document.createElement("div");
      group.className = "quiz-options";

      question.options.forEach(function (option, oIndex) {
        var id = "q" + qIndex + "-o" + oIndex;
        var label = document.createElement("label");
        label.className = "quiz-option";
        label.setAttribute("for", id);

        var input = document.createElement("input");
        input.type = "radio";
        input.name = "q" + qIndex;
        input.id = id;
        input.value = String(oIndex);

        var mark = document.createElement("span");
        mark.className = "quiz-radio";
        mark.setAttribute("aria-hidden", "true");

        var text = document.createElement("span");
        text.className = "quiz-option-text";
        text.textContent = option;

        label.appendChild(input);
        label.appendChild(mark);
        label.appendChild(text);
        group.appendChild(label);
      });

      fieldset.appendChild(group);
      els.form.appendChild(fieldset);
    });

    var best = bestScore(lesson);
    els.status.textContent = best > 0 ? "Best attempt: " + best + "/" + lesson.quiz.length : "Not attempted";
    els.status.classList.toggle("is-pass", isComplete(lesson));
    updateNextButton();
  }

  function updateNextButton() {
    var idx = lessonIndex(activeId);
    var hasNext = idx >= 0 && idx < lessons.length - 1;
    els.next.classList.toggle("is-hidden", !hasNext);
  }

  function renderProgress() {
    var done = completedCount();
    var total = lessons.length;
    els.progressText.textContent = done + "/" + total + " completed";
    els.progressBar.style.width = total ? (done / total) * 100 + "%" : "0%";
    els.scoreText.textContent = String(totalScore());
    els.best.textContent = String(bestScore(byId(activeId) || lessons[0]));
  }

  function render() {
    renderList();
    renderLesson();
    renderQuiz();
    renderProgress();
  }

  function submitQuiz() {
    var lesson = byId(activeId) || lessons[0];
    var correct = 0;
    var unanswered = 0;

    lesson.quiz.forEach(function (question, qIndex) {
      var picked = els.form.querySelector('input[name="q' + qIndex + '"]:checked');
      if (!picked) {
        unanswered += 1;
        return;
      }
      if (Number(picked.value) === question.answerIndex) correct += 1;
    });

    if (unanswered === lesson.quiz.length) {
      els.status.textContent = "Answer at least one question to score.";
      return;
    }

    var previous = bestScore(lesson);
    if (correct > previous) {
      state.scores[lesson.id] = correct;
      saveState();
    }

    var best = bestScore(lesson);
    var passed = best / lesson.quiz.length >= PASS_RATIO;
    els.status.textContent =
      "This attempt: " + correct + "/" + lesson.quiz.length +
      " — Best: " + best + "/" + lesson.quiz.length +
      (passed ? " ✓ Passed" : " (need " + Math.ceil(lesson.quiz.length * PASS_RATIO) + " to pass)");
    els.status.classList.toggle("is-pass", passed);

    renderList();
    renderProgress();
  }

  function goNext() {
    var idx = lessonIndex(activeId);
    if (idx < 0 || idx >= lessons.length - 1) return;
    activeId = lessons[idx + 1].id;
    state.lastLesson = activeId;
    saveState();
    render();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function resetProgress() {
    state = { scores: {}, lastLesson: activeId };
    saveState();
    render();
    els.status.textContent = "Progress reset for this browser.";
    els.status.classList.remove("is-pass");
  }

  if (els.submit) els.submit.addEventListener("click", submitQuiz);
  if (els.next) els.next.addEventListener("click", goNext);
  if (els.reset) els.reset.addEventListener("click", resetProgress);

  if (els.form) {
    els.form.addEventListener("submit", function (event) {
      event.preventDefault();
      submitQuiz();
    });
  }

  state.lastLesson = activeId;
  saveState();
  render();
})();
