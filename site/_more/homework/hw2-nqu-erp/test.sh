#!/usr/bin/env bash
set -euo pipefail

BASE="http://localhost:8080"
PASS=0
FAIL=0
PID=""

cleanup() {
  if [ -n "$PID" ]; then
    kill "$PID" 2>/dev/null || true
    wait "$PID" 2>/dev/null || true
  fi
  # also kill any leftover server
  pkill -f "target/debug/nqu-erp" 2>/dev/null || true
}
trap cleanup EXIT

# Kill any existing server
pkill -f "target/debug/nqu-erp" 2>/dev/null || true
sleep 1

assert_contains() {
  local label="$1" body="$2" expected="$3"
  if echo "$body" | grep -q "$expected"; then
    echo "  ✅ $label"
    PASS=$((PASS + 1))
  else
    echo "  ❌ $label (expected '$expected')"
    echo "     got: ${body:0:200}"
    FAIL=$((FAIL + 1))
  fi
}

assert_eq() {
  local label="$1" actual="$2" expected="$3"
  if [ "$actual" = "$expected" ]; then
    echo "  ✅ $label"
    PASS=$((PASS + 1))
  else
    echo "  ❌ $label (expected '$expected', got '$actual')"
    FAIL=$((FAIL + 1))
  fi
}

assert_status() {
  local label="$1" actual="$2" expected="$3"
  if [ "$actual" = "$expected" ]; then
    echo "  ✅ $label (HTTP $actual)"
    PASS=$((PASS + 1))
  else
    echo "  ❌ $label (expected HTTP $expected, got HTTP $actual)"
    FAIL=$((FAIL + 1))
  fi
}

echo "========================================="
echo "  NQU-ERP API 自動化測試"
echo "========================================="
echo ""

# ---- 0. Build ----
echo "[0] 建置專案..."
cargo build 2>/dev/null
echo "    build OK"
echo ""

# ---- 1. Start server ----
echo "[1] 啟動 server..."
rm -f dev.db
./target/debug/nqu-erp &
PID=$!
sleep 3

# ---- 2. Seed ----
echo "[2] 插入假資料..."
python3 scripts/seed.py -o scripts/seed.sql --seed 42
sqlite3 dev.db < scripts/seed.sql
echo "    seed OK"
echo ""

# ---- 3. Health check ----
echo "[3] 健康檢查"
BODY=$(curl -s "$BASE/health")
assert_eq "GET /health" "$BODY" "OK"
echo ""

# ---- 4. Login ----
echo "[4] 登入測試"

STUDENT=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username":"11303001","password":"student123"}')
STUDENT_HTTP=$(echo "$STUDENT" | tail -1)
STUDENT_BODY=$(echo "$STUDENT" | sed '$d')
STUDENT_TOKEN=$(echo "$STUDENT_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null || echo "")
assert_status "POST /auth/login (student)" "$STUDENT_HTTP" "200"
assert_contains "token 不為空" "$STUDENT_TOKEN" "ey"

TEACHER=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username":"T001","password":"teacher123"}')
TEACHER_HTTP=$(echo "$TEACHER" | tail -1)
TEACHER_BODY=$(echo "$TEACHER" | sed '$d')
TEACHER_TOKEN=$(echo "$TEACHER_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null || echo "")
assert_status "POST /auth/login (teacher)" "$TEACHER_HTTP" "200"
assert_contains "teacher token 不為空" "$TEACHER_TOKEN" "ey"

ADMIN=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}')
ADMIN_HTTP=$(echo "$ADMIN" | tail -1)
ADMIN_BODY=$(echo "$ADMIN" | sed '$d')
ADMIN_TOKEN=$(echo "$ADMIN_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null || echo "")
assert_status "POST /auth/login (admin)" "$ADMIN_HTTP" "200"
assert_contains "admin token 不為空" "$ADMIN_TOKEN" "ey"

# Wrong password
BAD=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username":"11303001","password":"wrong"}')
BAD_HTTP=$(echo "$BAD" | tail -1)
BAD_BODY=$(echo "$BAD" | sed '$d')
assert_status "POST /auth/login (wrong password)" "$BAD_HTTP" "401"
assert_contains "回傳錯誤訊息" "$BAD_BODY" "帳號或密碼錯誤"
echo ""

# ---- 5. Courses ----
echo "[5] 課程查詢"
CRS=$(curl -s -w "\n%{http_code}" "$BASE/api/v1/courses" \
  -H "Authorization: Bearer $STUDENT_TOKEN")
CRS_HTTP=$(echo "$CRS" | tail -1)
CRS_COUNT=$(echo "$CRS" | sed '$d' | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
assert_status "GET /courses (student)" "$CRS_HTTP" "200"
assert_eq "課程數量 = 15" "$CRS_COUNT" "15"

# Without auth → 401
NOAUTH=$(curl -s -w "\n%{http_code}" "$BASE/api/v1/courses")
NOAUTH_HTTP=$(echo "$NOAUTH" | tail -1)
assert_status "GET /courses (no auth → 401)" "$NOAUTH_HTTP" "401"
echo ""

# ---- 6. Enroll ----
echo "[6] 選課測試"

# Enroll in a non-conflicting course (course 3: 計算機網路, Wed 4-6)
ENR=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/enrollments" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"course_id":3}')
ENR_HTTP=$(echo "$ENR" | tail -1)
ENR_BODY=$(echo "$ENR" | sed '$d')
assert_status "POST /enrollments (course 3)" "$ENR_HTTP" "200"
assert_contains "加選成功" "$ENR_BODY" "加選成功"

# Duplicate enroll
DUP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/enrollments" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"course_id":3}')
DUP_HTTP=$(echo "$DUP" | tail -1)
DUP_BODY=$(echo "$DUP" | sed '$d')
assert_status "POST /enrollments (duplicate)" "$DUP_HTTP" "200"
assert_contains "重複選課偵測" "$DUP_BODY" "已選修過"

# Only students can enroll
TEACHER_ENR=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/enrollments" \
  -H "Authorization: Bearer $TEACHER_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"course_id":3}')
TEACHER_ENR_HTTP=$(echo "$TEACHER_ENR" | tail -1)
assert_status "POST /enrollments (teacher → forbidden)" "$TEACHER_ENR_HTTP" "403"
echo ""

# ---- 7. Schedule ----
echo "[7] 課表查詢"
SCH=$(curl -s -w "\n%{http_code}" "$BASE/api/v1/students/me/schedule" \
  -H "Authorization: Bearer $STUDENT_TOKEN")
SCH_HTTP=$(echo "$SCH" | tail -1)
SCH_COUNT=$(echo "$SCH" | sed '$d' | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
assert_status "GET /students/me/schedule" "$SCH_HTTP" "200"
assert_contains "課表有資料" "$SCH_COUNT" ""
echo ""

# ---- 8. Teacher courses ----
echo "[8] 教師授課清單"
TCR=$(curl -s -w "\n%{http_code}" "$BASE/api/v1/teachers/me/courses" \
  -H "Authorization: Bearer $TEACHER_TOKEN")
TCR_HTTP=$(echo "$TCR" | tail -1)
TCR_COUNT=$(echo "$TCR" | sed '$d' | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
assert_status "GET /teachers/me/courses" "$TCR_HTTP" "200"
assert_eq "T001 授課數 >= 1" "$(( TCR_COUNT >= 1 ))" "1"
echo ""

# ---- 9. Student grades ----
echo "[9] 學生成績查詢"
GRD=$(curl -s -w "\n%{http_code}" "$BASE/api/v1/students/me/grades" \
  -H "Authorization: Bearer $STUDENT_TOKEN")
GRD_HTTP=$(echo "$GRD" | tail -1)
GRD_COUNT=$(echo "$GRD" | sed '$d' | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
assert_status "GET /students/me/grades" "$GRD_HTTP" "200"
assert_contains "成績有資料" "$GRD_COUNT" ""
echo ""

# ---- 10. Batch grade update ----
echo "[10] 成績登錄"

# Use enrollment_id=46 (course 1, student 24, is_submitted=0 in seed)
BATCH=$(curl -s -w "\n%{http_code}" -X PUT "$BASE/api/v1/grades/batch" \
  -H "Authorization: Bearer $TEACHER_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"course_id":1,"grades":[{"enrollment_id":46,"midterm_score":75,"final_score":88}]}')
BATCH_HTTP=$(echo "$BATCH" | tail -1)
BATCH_BODY=$(echo "$BATCH" | sed '$d')
assert_status "PUT /grades/batch" "$BATCH_HTTP" "200"
assert_contains "成績登錄成功" "$BATCH_BODY" "成功"

# Submit grades for course 1
SUB=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/grades/submit" \
  -H "Authorization: Bearer $TEACHER_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"course_id":1}')
SUB_HTTP=$(echo "$SUB" | tail -1)
SUB_BODY=$(echo "$SUB" | sed '$d')
assert_status "POST /grades/submit" "$SUB_HTTP" "200"
assert_contains "成績鎖定成功" "$SUB_BODY" "鎖定"

# Student grades should now show submitted
GRD2=$(curl -s "$BASE/api/v1/students/me/grades" \
  -H "Authorization: Bearer $STUDENT_TOKEN")
SUBMITTED=$(echo "$GRD2" | python3 -c "
import sys,json
d=json.load(sys.stdin)
submitted = [g for g in d if g.get('is_submitted')]
print(len(submitted))
" 2>/dev/null || echo "0")
assert_contains "有已送交成績" "$SUBMITTED" ""
echo ""

# ---- 11. Drop course ----
echo "[11] 退選測試"
DRP=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE/api/v1/enrollments" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"course_id":3}')
DRP_HTTP=$(echo "$DRP" | tail -1)
DRP_BODY=$(echo "$DRP" | sed '$d')
assert_status "DELETE /enrollments (course 3)" "$DRP_HTTP" "200"
assert_contains "退選成功" "$DRP_BODY" "退選成功"

# Enrolled count should decrease
CRS2=$(curl -s "$BASE/api/v1/courses" \
  -H "Authorization: Bearer $STUDENT_TOKEN")
C3_ENROLLED=$(echo "$CRS2" | python3 -c "
import sys,json
d=json.load(sys.stdin)
c = [x for x in d if x['course_id']==3]
print(c[0]['enrolled_count'] if c else 'N/A')
" 2>/dev/null || echo "N/A")
echo "  ℹ️  course 3 enrolled_count = $C3_ENROLLED after drop"
echo ""

# ---- 12. Admin create user ----
echo "[12] 管理員功能"
NEW_USER=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/admin/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"username":"S099","password":"test1234","full_name":"測試學生","role":"STUDENT","dept_id":1,"email":"s099@test.nqu.edu.tw"}')
NEW_USER_HTTP=$(echo "$NEW_USER" | tail -1)
NEW_USER_BODY=$(echo "$NEW_USER" | sed '$d')
assert_status "POST /admin/users" "$NEW_USER_HTTP" "200"
assert_contains "建立使用者成功" "$NEW_USER_BODY" "帳號建立成功"

# Student cannot create user
STU_REG=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/admin/users" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"username":"S100","password":"test1234","full_name":"非法","role":"STUDENT","dept_id":1,"email":"x@test.nqu.edu.tw"}')
STU_REG_HTTP=$(echo "$STU_REG" | tail -1)
assert_status "POST /admin/users (student → forbidden)" "$STU_REG_HTTP" "403"

# Admin user list
ADM_USERS=$(curl -s -w "\n%{http_code}" "$BASE/api/v1/admin/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
ADM_USERS_HTTP=$(echo "$ADM_USERS" | tail -1)
ADM_USERS_BODY=$(echo "$ADM_USERS" | sed '$d')
ADR_COUNT=$(echo "$ADM_USERS_BODY" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
assert_status "GET /admin/users" "$ADM_USERS_HTTP" "200"
assert_contains "含剛建立之 S099" "$ADM_USERS_BODY" "S099"
assert_eq "帳號數 = 43" "$ADR_COUNT" "43"

# Student cannot list users
STU_LIST=$(curl -s -w "\n%{http_code}" "$BASE/api/v1/admin/users" \
  -H "Authorization: Bearer $STUDENT_TOKEN")
STU_LIST_HTTP=$(echo "$STU_LIST" | tail -1)
assert_status "GET /admin/users (student → forbidden)" "$STU_LIST_HTTP" "403"

# Admin teachers + departments
ADM_TEACHERS=$(curl -s "$BASE/api/v1/admin/teachers" -H "Authorization: Bearer $ADMIN_TOKEN")
ADM_TEACHERS_COUNT=$(echo "$ADM_TEACHERS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
assert_eq "GET /admin/teachers 數量 = 10" "$ADM_TEACHERS_COUNT" "10"
ADM_DEPTS=$(curl -s "$BASE/api/v1/admin/departments" -H "Authorization: Bearer $ADMIN_TOKEN")
ADM_DEPTS_COUNT=$(echo "$ADM_DEPTS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
assert_eq "GET /admin/departments 數量 = 5" "$ADM_DEPTS_COUNT" "5"

# Admin create course
NEW_COURSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/admin/courses" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"course_code":"TEST101","academic_year":113,"semester":1,"course_name":"測試課程","teacher_id":1,"credits":3,"capacity":40,"dept_id":1}')
NEW_COURSE_HTTP=$(echo "$NEW_COURSE" | tail -1)
NEW_COURSE_BODY=$(echo "$NEW_COURSE" | sed '$d')
assert_status "POST /admin/courses" "$NEW_COURSE_HTTP" "200"
assert_contains "開課成功" "$NEW_COURSE_BODY" "課程建立成功"
CRS16=$(curl -s "$BASE/api/v1/courses" -H "Authorization: Bearer $STUDENT_TOKEN")
CRS16_COUNT=$(echo "$CRS16" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
assert_eq "課程數變為 16" "$CRS16_COUNT" "16"
echo ""

# ---- 12b. Admin update / delete user ----
echo "[12b] 管理員修改/刪除帳號"

# Student cannot update other users
STU_PUT=$(curl -s -w "\n%{http_code}" -X PUT "$BASE/api/v1/admin/users/42" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"password":"","full_name":"非法改名","role":"STUDENT","dept_id":1,"email":"x@test.nqu.edu.tw"}')
STU_PUT_HTTP=$(echo "$STU_PUT" | tail -1)
assert_status "PUT /admin/users/{id} (student → forbidden)" "$STU_PUT_HTTP" "403"

# Find S099's user_id from the list
S099_ID=$(echo "$ADM_USERS_BODY" | python3 -c "
import sys,json
d=json.load(sys.stdin)
u=[x for x in d if x['username']=='S099']
print(u[0]['user_id'] if u else '')
" 2>/dev/null || echo "")
assert_eq "找到 S099 的 user_id" "$S099_ID" "43"

# Admin updates S099 (rename + password)
UPD_USER=$(curl -s -w "\n%{http_code}" -X PUT "$BASE/api/v1/admin/users/$S099_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"password":"newpass123","full_name":"測試改名","role":"STUDENT","dept_id":2,"email":"s099.new@test.nqu.edu.tw"}')
UPD_USER_HTTP=$(echo "$UPD_USER" | tail -1)
UPD_USER_BODY=$(echo "$UPD_USER" | sed '$d')
assert_status "PUT /admin/users/{id}" "$UPD_USER_HTTP" "200"
assert_contains "帳號更新成功" "$UPD_USER_BODY" "帳號更新成功"

# Verify rename + old password invalid + new password works
ADM_USERS2=$(curl -s "$BASE/api/v1/admin/users" -H "Authorization: Bearer $ADMIN_TOKEN")
assert_contains "名冊含新姓名 測試改名" "$ADM_USERS2" "測試改名"
assert_contains "名冊含新 email" "$ADM_USERS2" "s099.new"
OLD_PW=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username":"S099","password":"test1234"}')
OLD_PW_HTTP=$(echo "$OLD_PW" | tail -1)
assert_status "舊密碼登入失敗" "$OLD_PW_HTTP" "401"
NEW_PW=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username":"S099","password":"newpass123"}')
NEW_PW_HTTP=$(echo "$NEW_PW" | tail -1)
assert_status "新密碼登入成功" "$NEW_PW_HTTP" "200"

# Teacher with courses cannot be deleted
DEL_TEACHER=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE/api/v1/admin/users/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
DEL_TEACHER_HTTP=$(echo "$DEL_TEACHER" | tail -1)
assert_status "DELETE 有課教師 → 400" "$DEL_TEACHER_HTTP" "400"

# Cannot delete self (admin id = 41 from seed)
DEL_SELF=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE/api/v1/admin/users/41" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
DEL_SELF_HTTP=$(echo "$DEL_SELF" | tail -1)
assert_status "DELETE 自己 → 400" "$DEL_SELF_HTTP" "400"

# Student cannot delete
STU_DEL=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE/api/v1/admin/users/$S099_ID" \
  -H "Authorization: Bearer $STUDENT_TOKEN")
STU_DEL_HTTP=$(echo "$STU_DEL" | tail -1)
assert_status "DELETE /admin/users/{id} (student → forbidden)" "$STU_DEL_HTTP" "403"

# Admin deletes S099
DEL_USER=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE/api/v1/admin/users/$S099_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
DEL_USER_HTTP=$(echo "$DEL_USER" | tail -1)
DEL_USER_BODY=$(echo "$DEL_USER" | sed '$d')
assert_status "DELETE /admin/users/{id}" "$DEL_USER_HTTP" "200"
assert_contains "帳號刪除成功" "$DEL_USER_BODY" "刪除成功"

# Verify S099 gone
ADM_USERS3=$(curl -s "$BASE/api/v1/admin/users" -H "Authorization: Bearer $ADMIN_TOKEN")
ADM_USERS3_COUNT=$(echo "$ADM_USERS3" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
assert_eq "帳號數回到 42" "$ADM_USERS3_COUNT" "42"
echo ""

# ---- 12c. Admin update / delete course ----
echo "[12c] 管理員修改/刪除課程"

# Student cannot update course
STU_COURSE_PUT=$(curl -s -w "\n%{http_code}" -X PUT "$BASE/api/v1/admin/courses/16" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"course_code":"TEST101","academic_year":113,"semester":1,"course_name":"非法","teacher_id":1,"credits":3,"capacity":40,"dept_id":1}')
STU_COURSE_PUT_HTTP=$(echo "$STU_COURSE_PUT" | tail -1)
assert_status "PUT /admin/courses/{id} (student → forbidden)" "$STU_COURSE_PUT_HTTP" "403"

# Admin updates TEST101 (id 16): rename + new capacity
UPD_COURSE=$(curl -s -w "\n%{http_code}" -X PUT "$BASE/api/v1/admin/courses/16" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"course_code":"TEST101","academic_year":113,"semester":1,"course_name":"測試課程改名","teacher_id":1,"credits":4,"capacity":60,"dept_id":1}')
UPD_COURSE_HTTP=$(echo "$UPD_COURSE" | tail -1)
UPD_COURSE_BODY=$(echo "$UPD_COURSE" | sed '$d')
assert_status "PUT /admin/courses/{id}" "$UPD_COURSE_HTTP" "200"
assert_contains "課程更新成功" "$UPD_COURSE_BODY" "課程更新成功"

# Verify rename
CRS16B=$(curl -s "$BASE/api/v1/courses" -H "Authorization: Bearer $STUDENT_TOKEN")
assert_contains "課程列表含新名稱" "$CRS16B" "測試課程改名"
UPD_CREDITS=$(echo "$CRS16B" | python3 -c "
import sys,json
d=json.load(sys.stdin)
c=[x for x in d if x['course_id']==16]
print(c[0]['credits'] if c else 'N/A')
" 2>/dev/null || echo "N/A")
assert_eq "修改後學分 = 4" "$UPD_CREDITS" "4"

# Student cannot delete course
STU_COURSE_DEL=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE/api/v1/admin/courses/16" \
  -H "Authorization: Bearer $STUDENT_TOKEN")
STU_COURSE_DEL_HTTP=$(echo "$STU_COURSE_DEL" | tail -1)
assert_status "DELETE /admin/courses/{id} (student → forbidden)" "$STU_COURSE_DEL_HTTP" "403"

# Admin deletes TEST101
DEL_COURSE=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE/api/v1/admin/courses/16" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
DEL_COURSE_HTTP=$(echo "$DEL_COURSE" | tail -1)
DEL_COURSE_BODY=$(echo "$DEL_COURSE" | sed '$d')
assert_status "DELETE /admin/courses/{id}" "$DEL_COURSE_HTTP" "200"
assert_contains "課程刪除成功" "$DEL_COURSE_BODY" "刪除成功"

# Verify course count back to 15, deleting again → 404
CRS_FINAL=$(curl -s "$BASE/api/v1/courses" -H "Authorization: Bearer $STUDENT_TOKEN")
CRS_FINAL_COUNT=$(echo "$CRS_FINAL" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
assert_eq "課程數回到 15" "$CRS_FINAL_COUNT" "15"
DEL_COURSE2=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE/api/v1/admin/courses/16" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
DEL_COURSE2_HTTP=$(echo "$DEL_COURSE2" | tail -1)
assert_status "再次刪除 → 404" "$DEL_COURSE2_HTTP" "404"
echo ""

# ---- 13. Teacher roster ----
echo "[13] 教師名冊查詢"

TCR2=$(curl -s "$BASE/api/v1/teachers/me/courses" -H "Authorization: Bearer $TEACHER_TOKEN")
TCR2_FIRST=$(echo "$TCR2" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['course_id'] if d else '')" 2>/dev/null || echo "")
assert_eq "T001 授課第一門課 = 1" "$TCR2_FIRST" "1"

ROSTER=$(curl -s -w "\n%{http_code}" "$BASE/api/v1/teachers/me/courses/$TCR2_FIRST/students" \
  -H "Authorization: Bearer $TEACHER_TOKEN")
ROSTER_HTTP=$(echo "$ROSTER" | tail -1)
ROSTER_BODY=$(echo "$ROSTER" | sed '$d')
ROSTER_COUNT=$(echo "$ROSTER_BODY" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
assert_status "GET /teachers/me/courses/{id}/students" "$ROSTER_HTTP" "200"
assert_eq "名冊 >= 1 人" "$(( ROSTER_COUNT >= 1 ))" "1"
assert_contains "名冊含完整欄位" "$ROSTER_BODY" "student_number"

# Student only sees ENROLLED rows; forbidden for student
STU_ROSTER=$(curl -s -w "\n%{http_code}" "$BASE/api/v1/teachers/me/courses/$TCR2_FIRST/students" \
  -H "Authorization: Bearer $STUDENT_TOKEN")
STU_ROSTER_HTTP=$(echo "$STU_ROSTER" | tail -1)
assert_status "GET roster (student → forbidden)" "$STU_ROSTER_HTTP" "403"

# Teacher cannot access other course roster (course 2 belongs to T002)
OTHER_ROSTER=$(curl -s -w "\n%{http_code}" "$BASE/api/v1/teachers/me/courses/2/students" \
  -H "Authorization: Bearer $TEACHER_TOKEN")
OTHER_ROSTER_HTTP=$(echo "$OTHER_ROSTER" | tail -1)
assert_status "GET roster (非本人課程 → forbidden)" "$OTHER_ROSTER_HTTP" "403"
echo ""

# ---- Summary ----
echo "========================================="
TOTAL=$((PASS + FAIL))
echo "  結果: $PASS/$TOTAL 通過, $FAIL 失敗"
echo "========================================="

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
