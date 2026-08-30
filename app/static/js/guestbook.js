const form = document.getElementById("message-form");
const list = document.getElementById("message-list");

function escapeHtml(s) {
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  };
  return String(s).replace(/[&<>"']/g, (c) => map[c]);
}

async function loadMessages() {
  const res = await fetch("/api/messages");
  const data = await res.json();
  list.innerHTML = "";

  if (!data.messages || data.messages.length === 0) {
    list.innerHTML = '<p class="empty">还没有留言,来抢沙发吧~</p>';
    return;
  }

  for (const m of data.messages) {
    const div = document.createElement("div");
    div.className = "message";
    div.innerHTML =
      '<div class="msg-head">' +
      '<span class="nick">' + escapeHtml(m.nickname) + "</span>" +
      '<span class="time">' + escapeHtml(m.created_at) + "</span>" +
      "</div>" +
      '<div class="content">' + escapeHtml(m.content) + "</div>";
    list.appendChild(div);
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const nickname = document.getElementById("nickname").value.trim();
  const content = document.getElementById("content").value.trim();

  const res = await fetch("/api/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nickname, content }),
  });

  if (res.ok) {
    document.getElementById("nickname").value = "";
    document.getElementById("content").value = "";
    await loadMessages();
  } else {
    const err = await res.json();
    alert(err.error || "提交失败");
  }
});

loadMessages();
