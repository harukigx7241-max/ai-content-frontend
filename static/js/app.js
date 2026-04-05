const generateBtn = document.getElementById("generateBtn");
const resultEl = document.getElementById("result");

generateBtn.addEventListener("click", async () => {
  const theme = document.getElementById("theme").value.trim();
  const target = document.getElementById("target").value.trim();
  const tone = document.getElementById("tone").value.trim();

  if (!theme || !target || !tone) {
    alert("テーマ・ターゲット・文体をすべて入力してください。");
    return;
  }

  resultEl.value = "生成中...";

  try {
    const res = await fetch("/api/note/prompt", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        theme,
        target,
        tone
      })
    });

    if (!res.ok) {
      throw new Error("APIエラー");
    }

    const data = await res.json();
    resultEl.value = data.prompt || "";
  } catch (error) {
    console.error(error);
    resultEl.value = "エラーが発生しました。";
  }
});