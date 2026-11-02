import { useState } from "react";
import { Alert, Button, Card, Container, Group, Stack, Tabs, Text, TextInput, Textarea, Title } from "@mantine/core";

type Course = { course_id:number; course_code:string; title:string; description:string; syllabus:string; schedule:unknown[] };
const api = (courseId:number, suffix="") => `/api/v1/lms/courses/${courseId}${suffix}`;

export default function CoursesPage() {
  const [courseId,setCourseId]=useState("");
  const [course,setCourse]=useState<Course|null>(null);
  const [error,setError]=useState("");
  const [loading,setLoading]=useState(false);
  const [materials,setMaterials]=useState<any[]>([]);
  const [announcements,setAnnouncements]=useState<any[]>([]);
  const [assignments,setAssignments]=useState<any[]>([]);
  async function load() {
    const id=Number(courseId);
    if(!Number.isSafeInteger(id)||id<=0){setError("Enter a valid course ID.");return;}
    setLoading(true);setError("");
    try {
      const response=await fetch(api(id),{credentials:"include"});
      if(!response.ok) throw new Error((await response.json()).detail || "Unable to load course.");
      setCourse(await response.json());
      const [m,a,w]=await Promise.all(["/materials","/announcements","/assignments"].map(s=>fetch(api(id,s),{credentials:"include"})));
      if(!m.ok||!a.ok||!w.ok) throw new Error("Course loaded, but one or more course sections could not be retrieved.");
      setMaterials(await m.json());setAnnouncements(await a.json());setAssignments(await w.json());
    } catch(e) {setCourse(null);setError(e instanceof Error?e.message:"Request failed.");}
    finally {setLoading(false);}
  }
  return <Container size="lg" py="xl">
    <Stack gap="md">
      <Title order={2}>LMS Course Management</Title>
      <Text c="dimmed">Open a course workspace using its existing Fusion course ID.</Text>
      <Group align="end">
        <TextInput label="Course ID" value={courseId} onChange={e=>setCourseId(e.currentTarget.value)} placeholder="Enter course ID" />
        <Button onClick={load} loading={loading}>Open course</Button>
      </Group>
      {error && <Alert color="red">{error}</Alert>}
      {course && <>
        <Card withBorder>
          <Title order={3}>{course.course_code ? `${course.course_code} — ` : ""}{course.title}</Title>
          <Text>{course.description || "No course description has been added."}</Text>
        </Card>
        <Tabs defaultValue="materials">
          <Tabs.List>
            <Tabs.Tab value="materials">Materials ({materials.length})</Tabs.Tab>
            <Tabs.Tab value="announcements">Announcements ({announcements.length})</Tabs.Tab>
            <Tabs.Tab value="assignments">Assignments ({assignments.length})</Tabs.Tab>
          </Tabs.List>
          <Tabs.Panel value="materials" pt="md"><Stack>{materials.map(x=><Card withBorder key={x.id}><Text fw={600}>{x.title}</Text><Text size="sm" c="dimmed">{x.section} · {x.kind}</Text>{x.content && <Text>{x.content}</Text>}{x.url && <a href={x.url} target="_blank" rel="noreferrer">Open resource</a>}</Card>)}{!materials.length&&<Text c="dimmed">No published materials.</Text>}</Stack></Tabs.Panel>
          <Tabs.Panel value="announcements" pt="md"><Stack>{announcements.map(x=><Card withBorder key={x.id}><Text fw={600}>{x.title}</Text><Text>{x.body}</Text><Text size="xs" c="dimmed">{new Date(x.created_at).toLocaleString()}</Text></Card>)}{!announcements.length&&<Text c="dimmed">No announcements.</Text>}</Stack></Tabs.Panel>
          <Tabs.Panel value="assignments" pt="md"><Stack>{assignments.map(x=><Card withBorder key={x.id}><Text fw={600}>{x.title}</Text><Text>{x.instructions}</Text><Text size="sm" c="dimmed">Due: {new Date(x.due_at).toLocaleString()} · {x.points_possible} points</Text></Card>)}{!assignments.length&&<Text c="dimmed">No published assignments.</Text>}</Stack></Tabs.Panel>
        </Tabs>
      </>}
    </Stack>
  </Container>;
}
