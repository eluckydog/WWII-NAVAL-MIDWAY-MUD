(function() {
  const terminal = document.getElementById('terminal');
  const output = document.getElementById('output');
  const input = document.getElementById('command-input');
  const sendBtn = document.getElementById('send-btn');
  const statusEl = document.getElementById('connection-status');

  let ws = null;
  let connected = false;

  function addLine(cls, text) {
    const div = document.createElement('div');
    div.className = 'line ' + cls;
    div.textContent = text;
    output.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
  }

  function send(cmd) {
    if (ws && connected) {
      ws.send(cmd + '\n');
    } else {
      addLine('system', '> ' + cmd);
      handleCommand(cmd);
    }
  }

  function handleCommand(cmd) {
    const c = cmd.trim().toLowerCase();
    if (c === 'help' || c === 'h') {
      addLine('navy', '用法: 通过 telnet 连接服务器以获得完整体验。');
      addLine('navy', '  telnet 127.0.0.1 6666');
    } else if (c === 'clear') {
      output.innerHTML = '';
    } else {
      addLine('system', '未知命令。输入 help 查看帮助。');
    }
  }

  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      const cmd = this.value.trim();
      if (cmd) { send(cmd); this.value = ''; }
    }
  });
  sendBtn.addEventListener('click', function() {
    const cmd = input.value.trim();
    if (cmd) { send(cmd); input.value = ''; }
  });
  document.addEventListener('click', function() { input.focus(); });

  statusEl.textContent = 'Web演示模式';
  statusEl.style.background = '#3a2a1a';
  statusEl.style.color = '#ffa726';
  addLine('system', 'Web客户端已加载。使用 telnet 连接获得完整MUD体验。');
  addLine('system', '服务器地址: telnet 127.0.0.1 6666');
})();
