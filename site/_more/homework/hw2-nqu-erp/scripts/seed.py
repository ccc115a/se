#!/usr/bin/env python3
"""
金門大學校務系統 MVP 假資料產生器
產出 SQL INSERT 檔案，可塞入 SQLite 或 PostgreSQL
"""

import random
import argparse
from datetime import datetime
import bcrypt

# === 科系資料 ===
DEPARTMENTS = [
    ("CSIE", "資訊工程學系"),
    ("EE", "電機工程學系"),
    ("ME", "機械工程學系"),
    ("BA", "企業管理學系"),
    ("TM", "觀光管理學系"),
]

# === 教師資料 ===
TEACHERS = [
    ("T001", "王大明", "CSIE"),
    ("T002", "李小華", "CSIE"),
    ("T003", "張志偉", "EE"),
    ("T004", "陳美玲", "EE"),
    ("T005", "林俊傑", "ME"),
    ("T006", "黃雅芬", "ME"),
    ("T007", "劉建宏", "BA"),
    ("T008", "吳佳琳", "BA"),
    ("T009", "鄭明哲", "TM"),
    ("T010", "蔡雅婷", "TM"),
]

# === 學生資料 ===
STUDENTS = [
    ("11303001", "陳小明", "CSIE"),
    ("11303002", "林小華", "CSIE"),
    ("11303003", "張小強", "CSIE"),
    ("11303004", "王小美", "CSIE"),
    ("11303005", "李小莉", "CSIE"),
    ("11303006", "黃小偉", "CSIE"),
    ("11306001", "劉志豪", "EE"),
    ("11306002", "陳雅芳", "EE"),
    ("11306003", "林俊宏", "EE"),
    ("11306004", "張美玲", "EE"),
    ("11306005", "王建平", "EE"),
    ("11306006", "李小娟", "EE"),
    ("11308001", "黃志偉", "ME"),
    ("11308002", "林美慧", "ME"),
    ("11308003", "張家豪", "ME"),
    ("11308004", "陳小雲", "ME"),
    ("11308005", "王大同", "ME"),
    ("11308006", "李志明", "ME"),
    ("11312001", "劉美玲", "BA"),
    ("11312002", "陳建志", "BA"),
    ("11312003", "林小芬", "BA"),
    ("11312004", "張志豪", "BA"),
    ("11312005", "王美華", "BA"),
    ("11312006", "李建華", "BA"),
    ("11315001", "鄭小玲", "TM"),
    ("11315002", "蔡志偉", "TM"),
    ("11315003", "林美珍", "TM"),
    ("11315004", "張家榮", "TM"),
    ("11315005", "王小萍", "TM"),
    ("11315006", "李雅芳", "TM"),
]

# === 課程資料 ===
COURSES = [
    ("CSIE301", "資料結構", "CSIE", 3),
    ("CSIE302", "演算法", "CSIE", 3),
    ("CSIE401", "計算機網路", "CSIE", 3),
    ("CSIE402", "資料庫系統", "CSIE", 3),
    ("CSIE201", "程式設計", "CSIE", 3),
    ("EE301", "電路學", "EE", 3),
    ("EE302", "電子學", "EE", 3),
    ("EE401", "控制系統", "EE", 3),
    ("ME301", "機械設計", "ME", 3),
    ("ME302", "熱力學", "ME", 3),
    ("BA201", "企業管理", "BA", 3),
    ("BA301", "會計學", "BA", 3),
    ("BA302", "人力資源管理", "BA", 3),
    ("TM201", "觀光英語", "TM", 3),
    ("TM301", "旅館管理", "TM", 3),
]

# === 上課時間模板 ===
SCHEDULE_TEMPLATES = [
    (1, 2, 4, "理工大樓"),  # 週一 2-3 節
    (3, 4, 6, "理工大樓"),  # 週三 4-5 節
    (2, 1, 3, "管理大樓"),  # 週二 1-2 節
    (4, 3, 5, "管理大樓"),  # 週四 3-4 節
    (5, 6, 8, "人文大樓"),  # 週五 6-7 節
    (1, 6, 8, "人文大樓"),  # 週一 6-7 節
    (3, 8, 10, "理工大樓"), # 週三 8-9 節
    (2, 6, 8, "管理大樓"),  # 週二 6-7 節
    (4, 1, 3, "人文大樓"),  # 週四 1-2 節
    (5, 10, 12, "理工大樓"), # 週五 10-11 節
]

def simple_hash(password: str) -> str:
    """使用 bcrypt 雜湊密碼，與 Rust bcrypt 套件相容"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def generate_sql():
    lines = []
    lines.append("-- 金門大學校務系統 MVP 假資料")
    lines.append(f"-- 產生時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # === 1. 科系 ===
    lines.append("-- 科系資料")
    for i, (code, name) in enumerate(DEPARTMENTS, 1):
        lines.append(
            f"INSERT INTO departments (dept_id, dept_code, dept_name) VALUES ({i}, '{code}', '{name}');"
        )
    lines.append("")

    # === 2. 使用者 (教師) ===
    lines.append("-- 教師帳號 (密碼: teacher123)")
    for i, (username, name, dept_code) in enumerate(TEACHERS, 1):
        dept_id = [d[0] for d in DEPARTMENTS].index(dept_code) + 1
        pwd_hash = simple_hash("teacher123")
        email = f"{username.lower()}@nqu.edu.tw"
        lines.append(
            f"INSERT INTO users (user_id, username, password_hash, full_name, role, dept_id, email) "
            f"VALUES ({i}, '{username}', '{pwd_hash}', '{name}', 'TEACHER', {dept_id}, '{email}');"
        )
    lines.append("")

    # === 3. 使用者 (學生) ===
    lines.append("-- 學生帳號 (密碼: student123)")
    for i, (username, name, dept_code) in enumerate(STUDENTS, len(TEACHERS) + 1):
        dept_id = [d[0] for d in DEPARTMENTS].index(dept_code) + 1
        pwd_hash = simple_hash("student123")
        email = f"{username}@stu.nqu.edu.tw"
        lines.append(
            f"INSERT INTO users (user_id, username, password_hash, full_name, role, dept_id, email) "
            f"VALUES ({i}, '{username}', '{pwd_hash}', '{name}', 'STUDENT', {dept_id}, '{email}');"
        )
    lines.append("")

    # === 4. 使用者 (管理員) ===
    lines.append("-- 管理員帳號")
    admin_id_base = len(TEACHERS) + len(STUDENTS) + 1
    lines.append(
        f"INSERT INTO users (user_id, username, password_hash, full_name, role, dept_id, email) "
        f"VALUES ({admin_id_base}, 'admin', '{simple_hash('admin123')}', '系統管理員', 'ADMIN', 1, 'admin@nqu.edu.tw');"
    )
    lines.append(
        f"INSERT INTO users (user_id, username, password_hash, full_name, role, dept_id, email) "
        f"VALUES ({admin_id_base + 1}, 'dean', '{simple_hash('dean123')}', '教務長', 'ADMIN', 1, 'dean@nqu.edu.tw');"
    )
    lines.append("")

    # === 5. 課程 ===
    lines.append("-- 課程資料 (113學年第1學期)")
    teacher_map = {t[0]: i + 1 for i, t in enumerate(TEACHERS)}
    dept_map = {d[0]: i + 1 for i, d in enumerate(DEPARTMENTS)}

    course_records = []
    for i, (code, name, dept_code, credits) in enumerate(COURSES, 1):
        dept_teachers = [t for t in TEACHERS if t[2] == dept_code]
        teacher = random.choice(dept_teachers)
        teacher_id = teacher_map[teacher[0]]
        capacity = random.randint(30, 60)
        course_records.append((i, code, name, dept_code, teacher_id, credits, capacity, dept_map[dept_code]))
        lines.append(
            f"INSERT INTO courses (course_id, course_code, academic_year, semester, course_name, "
            f"teacher_id, credits, capacity, enrolled_count, dept_id) "
            f"VALUES ({i}, '{code}', 113, 1, '{name}', {teacher_id}, {credits}, {capacity}, 0, {dept_map[dept_code]});"
        )
    lines.append("")

    # === 6. 上課時間 ===
    lines.append("-- 上課時間")
    schedule_id = 1
    course_schedules = {}  # course_id -> [(day, start, end, location)]
    for course_id, code, name, dept_code, teacher_id, credits, capacity, dept_id in course_records:
        num_schedules = random.choice([1, 1, 2])  # 大多數 1 個時段，少數 2 個
        used_times = set()
        schedules = []
        for _ in range(num_schedules):
            available = [s for s in SCHEDULE_TEMPLATES
                        if (s[0], s[1]) not in used_times and (s[0], s[2]) not in used_times]
            if not available:
                available = SCHEDULE_TEMPLATES
            tmpl = random.choice(available)
            day, start, end, building = tmpl
            location = f"{building} {chr(64 + random.randint(1, 5))}{random.randint(201, 305)}"
            schedules.append((day, start, end, location))
            used_times.add((day, start))
            used_times.add((day, end))

        course_schedules[course_id] = schedules
        for day, start, end, location in schedules:
            lines.append(
                f"INSERT INTO class_schedules (schedule_id, course_id, day_of_week, start_period, end_period, location) "
                f"VALUES ({schedule_id}, {course_id}, {day}, {start}, {end}, '{location}');"
            )
            schedule_id += 1
    lines.append("")

    # === 7. 選課紀錄 ===
    lines.append("-- 選課紀錄")
    student_ids = list(range(len(TEACHERS) + 1, len(TEACHERS) + len(STUDENTS) + 1))
    enrollment_records = []
    enrollment_id = 1

    for student_id in student_ids:
        num_courses = random.randint(2, 4)
        available_courses = list(range(1, len(COURSES) + 1))
        enrolled_times = set()  # (day, period) 已佔用的時段
        selected = []

        for _ in range(num_courses):
            if not available_courses:
                break

            random.shuffle(available_courses)
            chosen = None
            for cid in available_courses:
                conflict = False
                for day, start, end, _ in course_schedules.get(cid, []):
                    for p in range(start, end + 1):
                        if (day, p) in enrolled_times:
                            conflict = True
                            break
                if not conflict:
                    chosen = cid
                    break

            if chosen:
                selected.append(chosen)
                available_courses.remove(chosen)
                for day, start, end, _ in course_schedules.get(chosen, []):
                    for p in range(start, end + 1):
                        enrolled_times.add((day, p))

        for course_id in selected:
            status = "ENROLLED" if random.random() > 0.1 else "DROPPED"
            lines.append(
                f"INSERT INTO enrollments (enrollment_id, student_id, course_id, status) "
                f"VALUES ({enrollment_id}, {student_id}, {course_id}, '{status}');"
            )
            enrollment_records.append((enrollment_id, student_id, course_id, status))
            enrollment_id += 1
    lines.append("")

    # === 8. 成績 ===
    lines.append("-- 成績資料")
    grade_id = 1
    for enr_id, student_id, course_id, status in enrollment_records:
        midterm = round(random.uniform(50.0, 98.0), 2)
        final = round(random.uniform(45.0, 100.0), 2)
        total = round(midterm * 0.4 + final * 0.6, 2)
        submitted = "TRUE" if random.random() > 0.3 else "FALSE"
        lines.append(
            f"INSERT INTO grades (grade_id, enrollment_id, midterm_score, final_score, total_score, is_submitted) "
            f"VALUES ({grade_id}, {enr_id}, {midterm}, {final}, {total}, {submitted});"
        )
        grade_id += 1
    lines.append("")

    # === 統計 ===
    lines.append("-- === 假資料統計 ===")
    lines.append(f"-- 科系: {len(DEPARTMENTS)} 筆")
    lines.append(f"-- 教師: {len(TEACHERS)} 筆")
    lines.append(f"-- 學生: {len(STUDENTS)} 筆")
    lines.append(f"-- 管理員: 2 筆")
    lines.append(f"-- 課程: {len(COURSES)} 筆")
    lines.append(f"-- 上課時間: {schedule_id - 1} 筆")
    lines.append(f"-- 選課紀錄: {enrollment_id - 1} 筆")
    lines.append(f"-- 成績: {grade_id - 1} 筆")
    lines.append("")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="金門大學校務系統 MVP 假資料產生器")
    parser.add_argument("-o", "--output", help="輸出 SQL 檔案路徑", default=None)
    parser.add_argument("--seed", type=int, help="隨機種子", default=None)
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    sql = generate_sql()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(sql)
        print(f"假資料已寫入: {args.output}")
    else:
        print(sql)

if __name__ == "__main__":
    main()
