# -*- coding: utf-8 -*-
"""Render n8n install/OAuth friction panels — Windows Korean fonts (Malgun Gothic)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
W, H = 1280, 720

# Windows 기본 한글 폰트 (우선순위)
KOREAN_FONTS = [
    r"C:\Windows\Fonts\malgun.ttf",  # 맑은 고딕
    r"C:\Windows\Fonts\malgunbd.ttf",
    r"C:\Windows\Fonts\NanumGothic.ttf",
    r"C:\Windows\Fonts\gulim.ttc",
]
KOREAN_BOLD = [
    r"C:\Windows\Fonts\malgunbd.ttf",
    r"C:\Windows\Fonts\NanumGothicBold.ttf",
    r"C:\Windows\Fonts\malgun.ttf",
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    paths = KOREAN_BOLD if bold else KOREAN_FONTS
    for p in paths:
        if Path(p).exists():
            try:
                if p.lower().endswith(".ttc"):
                    return ImageFont.truetype(p, size, index=0)
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    raise RuntimeError("No Korean-capable Windows font found (malgun.ttf)")


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt, max_w: float) -> list[str]:
    """Character wrap (works for Hangul + Latin)."""
    lines: list[str] = []
    line = ""
    for ch in text:
        test = line + ch
        if draw.textlength(test, font=fnt) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = ch
    if line:
        lines.append(line)
    return lines or [""]


def draw_terminal(title: str, lines: list[str], out_name: str, footer: str) -> None:
    img = Image.new("RGB", (W, H), (15, 17, 21))
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, W, 48], fill=(30, 34, 42))
    d.ellipse([16, 16, 32, 32], fill=(255, 95, 86))
    d.ellipse([40, 16, 56, 32], fill=(255, 189, 46))
    d.ellipse([64, 16, 80, 32], fill=(39, 201, 63))
    d.text((100, 12), title, fill=(220, 225, 235), font=font(20, True))

    f_body = font(18)
    y = 68
    pad = 28
    max_w = W - pad * 2

    for raw in lines:
        color = (200, 205, 215)
        low = raw.lower()
        if "err" in low or "error" in low or "failed" in low or "missing" in low or "차단" in raw or "403" in raw:
            color = (255, 130, 130)
        elif any(
            k in raw
            for k in ("OK", "Success", "accessible", "설치 성공", "ready", "connected", "성공")
        ):
            color = (120, 220, 160)
        elif raw.startswith("$") or raw.startswith("PS ") or raw.startswith(">"):
            color = (140, 185, 255)
        elif raw.startswith("#") or raw.startswith("//"):
            color = (130, 140, 160)

        for line in wrap_text(d, raw, f_body, max_w):
            d.text((pad, y), line, fill=color, font=f_body)
            y += 26
            if y > H - 80:
                break
        if y > H - 80:
            break

    d.rectangle([0, H - 52, W, H], fill=(24, 28, 36))
    d.text((pad, H - 38), footer, fill=(170, 180, 195), font=font(16))
    path = OUT / out_name
    img.save(path, "PNG")
    print("wrote", path, "font=malgun")


def draw_browser(
    title: str,
    headline: str,
    body_lines: list[str],
    out_name: str,
    footer: str,
    error: bool = True,
) -> None:
    img = Image.new("RGB", (W, H), (245, 246, 248))
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, W, 56], fill=(232, 234, 237))
    d.rounded_rectangle([80, 12, W - 80, 44], radius=16, fill=(255, 255, 255), outline=(200, 200, 200))
    d.text((100, 16), "accounts.google.com / oauth", fill=(90, 90, 90), font=font(15))

    d.rounded_rectangle([160, 90, W - 160, H - 90], radius=12, fill=(255, 255, 255), outline=(220, 220, 220))
    head_color = (180, 30, 30) if error else (20, 120, 60)
    d.text((200, 120), headline, fill=head_color, font=font(28, True))

    y = 180
    f_body = font(19)
    for line in body_lines:
        for wline in wrap_text(d, line, f_body, W - 400):
            d.text((200, y), wline, fill=(35, 35, 35), font=f_body)
            y += 30

    d.text((200, H - 130), title, fill=(100, 100, 100), font=font(15))
    d.rectangle([0, H - 52, W, H], fill=(30, 34, 42))
    d.text((28, H - 38), footer, fill=(200, 205, 215), font=font(16))
    path = OUT / out_name
    img.save(path, "PNG")
    print("wrote", path, "font=malgun")


def main() -> None:
    # verify font
    f = font(20)
    print("using font:", getattr(f, "path", f))

    draw_terminal(
        "n8n 설치 · node-gyp (세션 터미널 로그)",
        [
            "$ npm install n8n@2.31.5 --no-fund --no-audit",
            "",
            "npm error path ...\\node_modules\\isolated-vm",
            "npm error command failed",
            "npm error command ... node-gyp-build || node-gyp rebuild",
            "gyp info using node-gyp@8.4.1",
            "gyp info using node@25.8.2 | win32 | x64",
            "gyp ERR! find VS",
            "gyp ERR! find VS checking VS2022 (17.14) found",
            "gyp ERR! find VS - found Visual Studio C++ core features",
            "gyp ERR! find VS - found VC++ toolset: v143",
            "gyp ERR! find VS - missing any Windows SDK",
            "gyp ERR! find VS could not find a version of Visual Studio to use",
            "",
            "// 원인: isolated-vm 네이티브 빌드에 Windows SDK 필요 (세션 로그 원문)",
        ],
        "n8n_friction_01_windows_sdk_missing.png",
        "설치 마찰 1/4 · Windows SDK 부재 · 출처: 로컬 터미널 실행 로그",
    )

    draw_terminal(
        "winget · Windows SDK 설치 (세션 터미널 로그)",
        [
            "$ winget install --id Microsoft.WindowsSDK.10.0.26100 -e",
            "",
            "찾음 Windows Software Development Kit - Windows 10.0.26100.4188",
            "다운로드 중 winsdksetup.exe",
            "설치 관리자 해시를 확인했습니다.",
            "패키지 설치를 시작하는 중...",
            "설치 성공",
            "",
            "// 이후에도 node-gyp@8.4.1 은 Windows11SDK 패키지명을 인식 못 함",
            "gyp ERR! find VS - missing any Windows SDK  (재발)",
            "",
            "$ npm install -g node-gyp@11.2.0",
            "gyp info using node-gyp@11.2.0",
            "gyp info find VS using VS2022 ... found Windows SDK  (OK)",
            "",
            "$ node-gyp rebuild  # isolated-vm / sqlite3",
            "isolated-vm OK",
            "sqlite3 OK",
        ],
        "n8n_friction_02_sdk_and_nodegyp_fix.png",
        "설치 마찰 2/4 · SDK 설치 + node-gyp 11 재빌드 · 출처: 로컬 터미널 실행 로그",
    )

    draw_terminal(
        "n8n 셀프호스트 · 최초 기동 (세션 터미널 로그)",
        [
            "$ cd n8n-runtime",
            "$ npx n8n",
            "",
            "No encryption key found - Auto-generating and saving to: ...\\.n8n\\config",
            "Initializing n8n process",
            "n8n ready on ::, port 5678",
            "n8n Task Broker ready on 127.0.0.1, port 5679",
            "Version: 2.31.5",
            "",
            "Editor is now accessible via:",
            "http://localhost:5678",
            "",
            "// 가입만 하면 되는 SaaS(Make/Zapier)와 달리",
            "// 로컬 기동 + owner 계정 생성이 필요 (무료의 대가)",
        ],
        "n8n_friction_03_n8n_ready.png",
        "설치 마찰 3/4 · 로컬 기동 성공 · 출처: 로컬 터미널 실행 로그",
    )

    draw_browser(
        "OAuth 시도 1 · Google 오류 화면 재구성 (실측 문구)",
        "액세스 차단됨: 승인 오류",
        [
            "cho***45@gmail.com",
            "",
            "The OAuth client was not found.",
            "",
            "원인: Client ID 오타·다른 프로젝트·삭제된 클라이언트,",
            "또는 서비스 계정 이메일을 OAuth Client ID 칸에 넣은 경우.",
            "조치: Cloud Console에서 웹 클라이언트 재확인 후",
            "….apps.googleusercontent.com 형태 ID 사용.",
        ],
        "n8n_friction_04_oauth_client_not_found.png",
        "OAuth 마찰 1/3 · OAuth client was not found · 실측 오류 문구 재구성",
        error=True,
    )

    draw_browser(
        "OAuth 시도 2 · Google 오류 화면 재구성 (실측 문구)",
        "액세스 차단됨: 테스트 모드",
        [
            "cho***45@gmail.com",
            "",
            "n8n local은(는) Google 인증 절차를 완료하지 않았습니다.",
            "앱은 현재 테스트 중이며 개발자가 승인한 테스터만",
            "앱에 액세스할 수 있습니다. (403: access_denied)",
            "",
            "조치: OAuth 동의 화면 → 테스트 사용자에",
            "본인 Gmail 추가 후 재시도. 프로덕션 게시는 불필요.",
        ],
        "n8n_friction_05_oauth_test_users.png",
        "OAuth 마찰 2/3 · 테스트 사용자 미등록 · 실측 오류 문구 재구성",
        error=True,
    )

    draw_terminal(
        "n8n credentials · 연결 완료 (프로젝트 체크리스트)",
        [
            "# n8n → Credentials (구현 완료 시점)",
            "",
            "Google Sheets Trigger account",
            "  type: Google Sheets Trigger OAuth2 API",
            "  status: Account connected",
            "  OAuth Redirect: http://localhost:5678/rest/oauth2-credential/callback",
            "  Client ID: ****-****.apps.googleusercontent.com",
            "",
            "Google Sheets account",
            "  type: Google Sheets OAuth2 API   # Trigger와 타입 분리",
            "  status: Account connected",
            "  용도: Append ×3 (고액/일반/검토)",
            "",
            "OpenAI account",
            "  type: OpenAI API",
            "  status: Saved",
            "",
            "// 같은 Client ID/Secret이라도 n8n credential 타입은 두 개 필요",
        ],
        "n8n_friction_06_credentials_connected.png",
        "OAuth 마찰 3/3 · 이중 credential 연결 완료 · 프로젝트 체크리스트 기반",
    )

    panels = [
        "n8n_friction_01_windows_sdk_missing.png",
        "n8n_friction_02_sdk_and_nodegyp_fix.png",
        "n8n_friction_03_n8n_ready.png",
        "n8n_friction_04_oauth_client_not_found.png",
        "n8n_friction_05_oauth_test_users.png",
        "n8n_friction_06_credentials_connected.png",
    ]
    thumbs = [Image.open(OUT / p).resize((400, 225), Image.Resampling.LANCZOS) for p in panels]
    grid = Image.new("RGB", (1280, 720), (20, 22, 28))
    d = ImageDraw.Draw(grid)
    d.text(
        (24, 14),
        "n8n Self-host · 설치·OAuth 마찰 스토리보드 (실측 로그 기반 재구성)",
        fill=(230, 230, 235),
        font=font(22, True),
    )
    positions = [(20, 60), (440, 60), (860, 60), (20, 320), (440, 320), (860, 320)]
    labels = [
        "1 SDK 부재",
        "2 SDK + gyp11",
        "3 n8n 기동",
        "4 OAuth not found",
        "5 테스트 사용자 403",
        "6 credential 연결",
    ]
    for im, pos, lab in zip(thumbs, positions, labels):
        grid.paste(im, pos)
        d.rectangle([pos[0], pos[1] + 225, pos[0] + 400, pos[1] + 252], fill=(30, 34, 42))
        d.text((pos[0] + 10, pos[1] + 230), lab, fill=(190, 200, 210), font=font(15))
    grid.save(OUT / "n8n_setup_or_oauth.png", "PNG")
    print("wrote", OUT / "n8n_setup_or_oauth.png")

    # GIF: resize smaller for speed
    frames = []
    for p in panels:
        im = Image.open(OUT / p).convert("RGB").resize((960, 540), Image.Resampling.LANCZOS)
        frames.append(im.convert("P", palette=Image.Palette.ADAPTIVE, colors=128))
    gif_path = OUT / "n8n_setup_or_oauth.gif"
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=2200,
        loop=0,
        optimize=False,
    )
    print("wrote", gif_path)
    print("done")


if __name__ == "__main__":
    main()
