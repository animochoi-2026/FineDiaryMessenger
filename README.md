# 파인다이어리 발송시스템

Windows용 파인다이어리 발송시스템의 공식 배포 저장소입니다. 배포 파일과 사용 안내만 공개합니다.

## 다운로드

[최신 버전 다운로드](https://github.com/animochoi-2026/FineDiaryMessenger/releases/latest)

Assets에서 **FineDiaryMessenger-windows-x64.zip**을 다운로드하고 압축을 푼 뒤 **FineDiaryMessenger.exe**를 실행하세요. Windows 64비트용입니다.

## 기존 사용자

프로그램을 완전히 종료한 뒤 기존 설치 폴더를 백업하고 ZIP 안의 FineDiaryMessenger 폴더 내용을 기존 설치 폴더에 복사하세요. **config.json, chrome_profile, data는 삭제하지 마세요.** 배포 ZIP에는 이 개인 데이터가 포함되지 않습니다.

v9 이전 버전에서는 이번 버전을 한 번 수동 설치해야 합니다. v10부터는 프로그램 상단의 **업데이트** 버튼으로 새 버전을 확인하고 설치할 수 있습니다. 기본 GitHub 저장소는 이미 지정되어 있습니다.

## 업데이트 동작

- 사용자가 업데이트 확인을 누를 때 GitHub 정식 릴리즈를 조회합니다.
- 다운로드 파일의 SHA-256과 패키지 구조를 검증합니다.
- 종료 후 프로그램 파일만 교체하며 기존 설정·학생 이미지·로그인 프로필을 유지합니다.
- 교체 실패 시 이전 프로그램 파일 복구를 시도합니다.
- 이전 파일은 설치 폴더의 `.update-backup-.../old`에 남습니다. 정상 동작 확인 후 정리할 수 있습니다.

GitHub에 학생 명단, 이미지, 설정 파일이나 Chrome 프로필을 올리지 마세요.
