async function sendMessage() {
  const subject = document.getElementById("subject").value;
  const content = document.getElementById("content").value;
  const sender = document.getElementById("sender").value;
  const recipient = document.getElementById("recipient").value;
  const origin = window.location.hostname;
  let destination = document.getElementById("destination").value;
  const timestamp = Date.now();

  if (!subject || !content || !sender || !recipient || !destination) {
    alert("Please fill out all fields.");
    return;
  }

  destination = destination.replace("http://", "").replace("https://", "").replace(/\/+$/, "");
  for (const host of [origin, destination]) {
    try {
      const response = await fetch(`https://${host}/api/receive`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          subject,
          content,
          sender,
          recipient,
          origin,
          destination,
          timestamp,
        }),
      });

      if (!response.ok) {
        throw new Error(response.statusText);
      }
    } catch (err) {
      alert(`Error sending message. ${err}`);
      return;
    }
  }

  const button = document.getElementById("send-button");
  button.textContent = "Sent!";
  button.style.backgroundColor = "var(--secondary)";
  setTimeout(() => (window.location = "/sent"), 1000);
}

async function showMessage(id) {
  const messageItem = document.getElementById(id);
  const subject = document.getElementById("subject");
  const content = document.getElementById("content");
  const sender = document.getElementById("sender");
  const recipient = document.getElementById("recipient");
  const origin = document.getElementById("origin");
  const destination = document.getElementById("destination");
  const timestamp = document.getElementById("timestamp");

  const response = await fetch(`/api/message/${id}`);
  const message = await response.json();
  const date = new Date(message.timestamp);
  const dateString = date.toLocaleString(undefined, {
    day: "numeric",
    weekday: "long",
    month: "long",
    year: "numeric",
    hour: "numeric",
    minute: "numeric",
    second: "numeric",
    timeZoneName: "short",
  });

  messageItem.setAttribute("data-read", "true");
  subject.textContent = message.subject;
  content.textContent = message.content;
  sender.textContent = message.sender;
  recipient.textContent = message.recipient;
  origin.textContent = message.origin;
  destination.textContent = message.destination;
  timestamp.textContent = dateString;
}
