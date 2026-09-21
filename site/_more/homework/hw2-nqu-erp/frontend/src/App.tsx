import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import PrivateRoute from './components/PrivateRoute'
import AdminCourses from './pages/AdminCourses'
import AdminUsers from './pages/AdminUsers'
import CourseList from './pages/CourseList'
import Login from './pages/Login'
import MyGrades from './pages/MyGrades'
import MySchedule from './pages/MySchedule'
import TeacherCourses from './pages/TeacherCourses'
import TeacherGradeEntry from './pages/TeacherGradeEntry'

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<PrivateRoute roles={['STUDENT']} />}>
          <Route path="/courses" element={<CourseList />} />
          <Route path="/schedule" element={<MySchedule />} />
          <Route path="/grades" element={<MyGrades />} />
        </Route>
        <Route element={<PrivateRoute roles={['TEACHER']} />}>
          <Route path="/teacher/courses" element={<TeacherCourses />} />
          <Route path="/teacher/courses/:courseId" element={<TeacherGradeEntry />} />
        </Route>
        <Route element={<PrivateRoute roles={['ADMIN']} />}>
          <Route path="/admin/users" element={<AdminUsers />} />
          <Route path="/admin/courses" element={<AdminCourses />} />
        </Route>
        <Route path="*" element={<Navigate to="/courses" replace />} />
      </Routes>
    </BrowserRouter>
  )
}