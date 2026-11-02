import { lazy } from "react";
import { Navigate, type RouteObject } from "react-router-dom";
const CoursesPage = lazy(() => import("./pages/CoursesPage"));
export const routes: RouteObject[] = [
  { index: true, element: <Navigate to="courses" replace /> },
  { path: "courses", element: <CoursesPage /> },
];
