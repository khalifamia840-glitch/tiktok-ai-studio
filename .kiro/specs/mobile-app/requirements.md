# Requirements Document

## Introduction

App móvil nativa para Android e iOS construida con React Native + Expo que replica y extiende la funcionalidad del frontend web de TikTok AI Studio. La app permite a los usuarios generar videos con IA, monitorear el progreso de generación, reproducir y compartir los videos resultantes, y gestionar su biblioteca de videos. Se conecta al backend FastAPI desplegado en `https://tiktok-ai-studio.onrender.com`.

## Glossary

- **App**: La aplicación móvil React Native + Expo descrita en este documento.
- **Backend**: El servidor FastAPI desplegado en `https://tiktok-ai-studio.onrender.com`.
- **Job**: Tarea de generación de video identificada por un `job_id` único.
- **Job_Status**: Estado de un Job; puede ser `pending`, `running`, `completed` o `error`.
- **Video**: Archivo MP4 generado por el Backend y almacenado en el servidor.
- **Library**: Colección de Videos generados disponibles en el Backend.
- **API_Client**: Módulo de la App responsable de todas las comunicaciones HTTP con el Backend.
- **Generate_Screen**: Pantalla de la App donde el usuario configura y lanza la generación de un Video.
- **Library_Screen**: Pantalla de la App donde el usuario visualiza, reproduce y gestiona su Library.
- **Tab_Bar**: Barra de navegación inferior de la App con acceso a Generate_Screen y Library_Screen.
- **Poller**: Mecanismo de la App que consulta periódicamente el estado de un Job activo.
- **Video_Player**: Componente de la App que reproduce Videos usando expo-av.
- **Progress_Bar**: Componente visual que muestra el porcentaje de avance de un Job.

---

## Requirements

### Requirement 1: Configuración y estructura del proyecto

**User Story:** As a developer, I want a properly scaffolded Expo project inside `mobile/`, so that I can build and run the app on Android and iOS without additional setup.

#### Acceptance Criteria

1. THE App SHALL be initialized as an Expo project using the latest stable SDK inside the `mobile/` directory at the root of the repository.
2. THE App SHALL use Expo Router for file-based navigation.
3. THE App SHALL declare all required dependencies in `mobile/package.json`, including `expo`, `expo-router`, `axios`, `expo-av`, `expo-file-system`, and `expo-sharing`.
4. THE App SHALL include an `app.json` with `name`, `slug`, `scheme`, `android` and `ios` platform configurations.
5. THE API_Client SHALL store the Backend base URL as a constant (`https://tiktok-ai-studio.onrender.com`) configurable via environment variable.

---

### Requirement 2: Navegación con Tab Bar

**User Story:** As a user, I want a bottom tab bar with two tabs, so that I can switch between generating videos and viewing my library.

#### Acceptance Criteria

1. THE Tab_Bar SHALL display two tabs: "Crear" (Generate_Screen) and "Biblioteca" (Library_Screen).
2. THE Tab_Bar SHALL use icons representing each tab: a video/sparkles icon for "Crear" and a film/library icon for "Biblioteca".
3. WHEN a tab is active, THE Tab_Bar SHALL highlight the active tab icon and label with color `#fe2c55`.
4. WHEN a tab is inactive, THE Tab_Bar SHALL render the tab icon and label in color `#555555`.
5. THE Tab_Bar SHALL have a background color of `#010101` and a top border of color `#1a1a1a`.
6. THE App SHALL render the Tab_Bar on both Android and iOS without platform-specific layout issues.

---

### Requirement 3: Pantalla de Generación de Video

**User Story:** As a user, I want to fill out a form and generate a TikTok-style video with AI, so that I can create content without manual editing.

#### Acceptance Criteria

1. THE Generate_Screen SHALL display a text input field for the video topic with a maximum length of 200 characters.
2. THE Generate_Screen SHALL display a selector for "Estilo" with options: `entretenido`, `educativo`, `motivacional`, `humor`, `misterio`, `viral`.
3. THE Generate_Screen SHALL display a selector for "Nicho" with options: `general`, `fitness`, `tecnologia`, `negocios`, `humor`, `educacion`, `lifestyle`, `salud`, `viajes`, `cocina`.
4. THE Generate_Screen SHALL display toggle buttons for "Duración" with values `15s`, `30s`, `60s`; the selected value SHALL be highlighted with background color `#fe2c55`.
5. THE Generate_Screen SHALL display toggle buttons for "Idioma" with values `ES` and `EN`; the selected value SHALL be highlighted with background color `#25f4ee` and black text.
6. THE Generate_Screen SHALL display a selector for "Voz" with options `edge` (Edge TTS) and `gtts` (Google TTS).
7. THE Generate_Screen SHALL display a toggle switch for "Agregar subtítulos" with active color `#fe2c55`.
8. WHEN the topic field is empty, THE Generate_Screen SHALL disable the submit button.
9. WHEN the user submits the form, THE API_Client SHALL send a POST request to `/api/generate` with fields `topic`, `style`, `audience`, `duration`, `language`, `voice`, `add_subtitles`, and `niche`.
10. IF the POST request to `/api/generate` fails, THEN THE Generate_Screen SHALL display the error message returned by the Backend or a fallback message "Error al iniciar la generación".

---

### Requirement 4: Polling del estado del Job

**User Story:** As a user, I want to see real-time progress while my video is being generated, so that I know when it will be ready.

#### Acceptance Criteria

1. WHEN a Job is created successfully, THE Poller SHALL begin querying `GET /api/status/{job_id}` every 2000 milliseconds.
2. WHILE a Job has Job_Status `pending` or `running`, THE Generate_Screen SHALL display a Progress_Bar showing the `progress` percentage and the `message` field from the Backend response.
3. THE Progress_Bar SHALL use a gradient from `#fe2c55` to `#25f4ee` to fill the completed portion.
4. WHEN the Job_Status becomes `completed`, THE Poller SHALL stop polling and THE Generate_Screen SHALL display the Video_Player with the generated Video.
5. WHEN the Job_Status becomes `error`, THE Poller SHALL stop polling and THE Generate_Screen SHALL display the error message from the Backend response.
6. IF the polling request to `/api/status/{job_id}` fails with a network error, THEN THE Poller SHALL stop and THE Generate_Screen SHALL display "Error al consultar el estado del video".
7. WHEN the Generate_Screen is unmounted while polling is active, THE Poller SHALL be cancelled to prevent memory leaks.

---

### Requirement 5: Reproducción de Video en Generate Screen

**User Story:** As a user, I want to preview the generated video directly in the app, so that I can verify the result before downloading.

#### Acceptance Criteria

1. WHEN a Job completes successfully, THE Video_Player SHALL render within the Generate_Screen using `expo-av`.
2. THE Video_Player SHALL support play, pause, and seek controls.
3. THE Video_Player SHALL display the video in a rounded container with black background.
4. WHEN the video is ready, THE Generate_Screen SHALL display a "Descargar MP4" button below the Video_Player.
5. WHEN the user taps "Descargar MP4", THE App SHALL download the Video file to the device using `expo-file-system` and confirm success with an alert.
6. IF the download fails, THEN THE App SHALL display an error alert with the message "Error al descargar el video".
7. WHERE the device supports sharing, THE Generate_Screen SHALL display a "Compartir" button that opens the native share sheet via `expo-sharing`.

---

### Requirement 6: Pantalla de Biblioteca

**User Story:** As a user, I want to browse all my generated videos in a list, so that I can replay or delete them.

#### Acceptance Criteria

1. WHEN the Library_Screen mounts, THE API_Client SHALL send a GET request to `/api/videos` and THE Library_Screen SHALL display the returned list of Videos.
2. WHILE the Library_Screen is loading videos, THE Library_Screen SHALL display a loading spinner.
3. WHEN the video list is empty, THE Library_Screen SHALL display an empty-state message: "No hay videos aún. Genera tu primer video en la pestaña Crear."
4. THE Library_Screen SHALL display each Video in a card showing: the Video_Player (using `expo-av`), the filename, and the file size in MB.
5. THE Library_Screen SHALL display a refresh button that re-fetches the video list from the Backend.
6. WHEN the user taps the delete button on a Video card, THE Library_Screen SHALL display a confirmation modal before deleting.
7. WHEN the user confirms deletion, THE API_Client SHALL send a DELETE request to `/api/videos/{filename}` and THE Library_Screen SHALL remove the deleted Video from the list without a full reload.
8. IF the DELETE request fails, THEN THE Library_Screen SHALL display an error alert with the message "Error al eliminar el video".
9. WHERE the device supports sharing, each Video card SHALL display a share button that opens the native share sheet via `expo-sharing`.

---

### Requirement 7: Diseño visual estilo TikTok

**User Story:** As a user, I want the app to have a dark TikTok-style design, so that it feels native and consistent with the brand.

#### Acceptance Criteria

1. THE App SHALL use `#010101` as the global background color for all screens.
2. THE App SHALL use `#fe2c55` as the primary accent color for active states, buttons, and highlights.
3. THE App SHALL use `#25f4ee` as the secondary accent color for language toggles and gradient endpoints.
4. THE App SHALL use white (`#ffffff`) for primary text and `#aaaaaa` for secondary/placeholder text.
5. THE App SHALL use `#1a1a1a` for card and input backgrounds, and `#2a2a2a` for borders.
6. THE App SHALL display a header with the "TikTok AI" logo (gradient icon + styled text) on all screens.
7. THE App SHALL use rounded corners (border-radius 12–16px) for all cards, inputs, and buttons.
8. THE App SHALL apply consistent horizontal padding of 16px on all screen content.

---

### Requirement 8: Manejo de conectividad y errores de red

**User Story:** As a user, I want the app to handle network errors gracefully, so that I understand what went wrong and can retry.

#### Acceptance Criteria

1. THE API_Client SHALL set a request timeout of 300000 milliseconds (5 minutes) for the `/api/generate` endpoint to accommodate long generation times.
2. THE API_Client SHALL set a request timeout of 10000 milliseconds for all other endpoints.
3. IF a request times out, THEN THE App SHALL display a user-friendly message: "La solicitud tardó demasiado. Verifica tu conexión e intenta de nuevo."
4. IF the Backend returns an HTTP error response, THEN THE App SHALL display the `detail` field from the response body, or a generic fallback message if `detail` is absent.
5. THE App SHALL support both absolute URLs (starting with `http://` or `https://`) and relative paths when constructing Video URLs, prepending the Backend base URL for relative paths.
