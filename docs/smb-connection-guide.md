# SMB/CIFS Access Guide for `\\172.16.16.159\Users\Sane Alam\Documents\MIS_DATA`

Use this checklist to mount the NAS share from Windows, WSL2, or Docker (CIFS). Replace `YOUR_USERNAME` with the account that works with password `wildnet`.

---

## 1) Quick Info to Collect
- Server: `172.16.16.159`
- Share: `Users/Sane Alam/Documents/MIS_DATA`
- Username: **YOUR_USERNAME** (the account that accepts password `wildnet`)
- Password: `wildnet`

If the username is unknown, temporarily copy one MIS Excel file locally (e.g., `dashboard/sample_data/`) and mount that folder while we obtain the correct credentials.

---

## 2) Test from Windows (File Explorer)
1. Press `Win+R` → enter `\\172.16.16.159\Users\Sane Alam\Documents\MIS_DATA` → OK.
2. If prompted, choose **Use different credentials** and enter:
   - Username: `YOUR_USERNAME`
   - Password: `wildnet`
3. If it opens, the credentials are correct; proceed to WSL/Docker.

---

## 3) Mount in WSL2 (temporary mount)
```bash
# Create mount point
sudo mkdir -p /mnt/mis_data

# Mount with CIFS
sudo mount -t cifs \
  -o username=YOUR_USERNAME,password=wildnet,uid=$(id -u),gid=$(id -g),file_mode=0644,dir_mode=0755,vers=3.0 \
  //172.16.16.159/Users/Sane\040Alam/Documents/MIS_DATA /mnt/mis_data

# Verify
ls /mnt/mis_data | head
```
If you get `Permission denied`, the username is incorrect or the NAS blocks the account. Confirm the exact username used on Windows.

---

## 4) Docker Compose (CIFS volume)
Add a named volume with CIFS options, then mount to the app at `/data`.

```yaml
# docker-compose.yml (snippet)
version: "3.9"
services:
  dashboard:
    build: ./dashboard
    volumes:
      - misdata:/data
    environment:
      - TZ=Asia/Kolkata
    ports:
      - "8501:8501"

volumes:
  misdata:
    driver: local
    driver_opts:
      type: cifs
      o: username=${SMB_USERNAME},password=${SMB_PASSWORD},vers=3.0,file_mode=0644,dir_mode=0755
      device: //172.16.16.159/Users/Sane\040Alam/Documents/MIS_DATA
```

Create a `.env` next to `docker-compose.yml`:
```
SMB_USERNAME=YOUR_USERNAME
SMB_PASSWORD=wildnet
```
Run `docker compose up -d` and check inside the container:
```bash
docker compose exec dashboard ls /data | head
```

---

## 5) Common Errors
- **Permission denied**: Wrong username or share disallows that account; verify the exact Windows-validated username.
- **Host is down / No route**: Ensure VPN/LAN connectivity to `172.16.16.159`.
- **vers mismatch**: Try `vers=2.1` or `vers=3.1.1` if `3.0` fails.
- **Space in path**: Use `Sane\040Alam` or quote the path when specifying device.

---

## 6) Fallback: Local Copy Workflow
If credentials are pending, copy one MIS Excel locally and mount that folder:
```bash
# Copy from Windows to project
# Example path: C:\Users\Dev Khairpal\Documents\Github\Tally-MIS\dashboard\sample_data\MIS_Report_Test.xlsx

# In docker-compose.yml, mount local folder instead of CIFS
services:
  dashboard:
    volumes:
      - ./dashboard/sample_data:/data:ro
```
Point the dashboard or scripts to `/data/MIS_Report_Test.xlsx` until CIFS credentials are confirmed.

---

## 7) What I Need From You
Please provide the exact username that works with password `wildnet` for the share `\\172.16.16.159\Users\Sane Alam\Documents\MIS_DATA`. Once I have it, I’ll finalize the CIFS mount and validate files appear in `/data`.

---

## 8) How to Grab Excel Headers for Debugging
If the dashboard cannot read `MIS_MIS_Report_20260115_112244_20260115_112259.xlsx`, grab the first-row headers so we can update the loader mappings.

- **Windows (PowerShell)**
  ```powershell
  $Path = "\\172.16.16.159\Users\Sane Alam\Documents\MIS_DATA\MIS_MIS_Report_20260115_112244_20260115_112259.xlsx"
  $Sheet = "Transactions"  # Try Transactions, Report, Data, Sheet1
  Import-Module ImportExcel
  (Get-ExcelSheetInfo -Path $Path).WorksheetName          # list sheets
  (Import-Excel -Path $Path -WorksheetName $Sheet -StartRow 1 -EndRow 1 | Get-Member -MemberType NoteProperty).Name
  ```
  Share the printed list of column names (or a screenshot). If `ImportExcel` is missing: `Install-Module -Name ImportExcel -Scope CurrentUser`.

- **WSL2/Linux (Python + pandas)**
  ```bash
  python - <<'PY'
  import pandas as pd
  path = "/mnt/mis_data/MIS_MIS_Report_20260115_112244_20260115_112259.xlsx"
  candidates = ["Transactions", "Report", "Data", "Sheet1"]
  xl = pd.ExcelFile(path)
  print("Sheets:", xl.sheet_names)
  for name in candidates:
      if name in xl.sheet_names:
          df = xl.parse(name, nrows=5)
          print(f"\nSheet: {name}")
          print("Headers:", list(df.columns))
          print(df.head())
  PY
  ```

If debit/credit are split (e.g., `Debit`, `Credit`, or `Amount Dr/Cr`), or dates differ (`Voucher Date` vs `Date`), include that detail. With the headers, I’ll align the loader to the sheet name and combine debit/credit if needed.
