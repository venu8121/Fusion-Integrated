import { useState } from "react";
import { Alert, Button, Card, Container, Group, Stack, Tabs, Text, TextInput, Title } from "@mantine/core";

type Course = {
  course_code: string;
  title: string;
  description: string;
  syllabus: string;
};

export default function CoursesPage() {
  const [courseId, setCourseId] = useState("");
  const [course, setCourse] = useState<Course | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function openCourse() {
    if (!/^\d+$/.test(courseId.trim())) {
      setError("Enter a valid numeric course ID.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`/api/v1/lms/courses/${courseId.trim()}`, {
        credentials: "include",
      });
      if (!response.ok) throw new Error("Course could not be opened. Check your course access.");
      setCourse(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed.");
      setCourse(null);
    } finally {
      setLoading(false);
    }
  }

  return <Container size="lg"><Stack gap="lg">
    <div><Title order={2}>LMS Course Management</Title>
      <Text c="dimmed">Open a course using its existing Fusion course ID.</Text></div>
    <Card withBorder><Group align="end">
      <TextInput label="Course ID" value={courseId}
        onChange={(event) => setCourseId(event.currentTarget.value)}
        placeholder="Enter course ID" />
      <Button onClick={openCourse} loading={loading}>Open course</Button>
    </Group></Card>
    {error && <Alert color="red">{error}</Alert>}
    {course && <Card withBorder><Stack>
      <Text size="sm" c="dimmed">{course.course_code}</Text>
      <Title order={3}>{course.title}</Title><Text>{course.description}</Text>
      <Tabs defaultValue="overview"><Tabs.List>
        <Tabs.Tab value="overview">Overview</Tabs.Tab>
        <Tabs.Tab value="materials">Materials</Tabs.Tab>
        <Tabs.Tab value="announcements">Announcements</Tabs.Tab>
        <Tabs.Tab value="assignments">Assignments</Tabs.Tab>
        <Tabs.Tab value="grades">Grades</Tabs.Tab>
      </Tabs.List>
      <Tabs.Panel value="overview" pt="md"><Title order={5}>Syllabus</Title>
        <Text>{course.syllabus || "No syllabus published."}</Text></Tabs.Panel>
      {["materials", "announcements", "assignments", "grades"].map((name) =>
        <Tabs.Panel value={name} pt="md" key={name}>
          <Text c="dimmed">Course {name} are available through the LMS API.</Text>
        </Tabs.Panel>)}
      </Tabs>
    </Stack></Card>}
  </Stack></Container>;
}
