# Implementation Plan: Mobile App — TikTok AI Studio

## Overview

Implementación de la app móvil React Native + Expo SDK 52 en `mobile/` usando Expo Router para navegación, axios para HTTP, y expo-av para reproducción de video. La app replica la funcionalidad del frontend web y se conecta al backend FastAPI.

## Tasks

- [x] 1. Set up project structure and configuration files
  - Create `mobile/app.json` with Expo configuration (name, slug, scheme, platform configs)
  - Create `mobile/package.json` with all required dependencies
  - Create `mobile/tsconfig.json` with TypeScript configuration for Expo
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Implement constants and API client
  - [x] 2.1 Create `mobile/lib/constants.ts` with COLORS, options arrays, and URL constants
    - Define COLORS object with all brand colors
    - Define STYLES_OPTIONS, NICHE_OPTIONS, DURATION_OPTIONS, VOICE_OPTIONS
    - _Requirements: 1.5, 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x] 2.2 Create `mobile/lib/api.ts` with axios instances and all API functions
    - Create two axios instances: `generateApi` (timeout 300000ms) and `api` (timeout 10000ms)
    - Add response interceptor for timeout and HTTP error handling
    - Implement `generateVideo`, `getJobStatus`, `listVideos`, `deleteVideo`, `getVideoUrl`
    - _Requirements: 1.5, 8.1, 8.2, 8.3, 8.4, 8.5_

  - [ ]* 2.3 Write property test for HTTP error message extraction (Property 8)
    - **Property 8: HTTP error message extraction**
    - **Validates: Requirements 8.4**

  - [ ]* 2.4 Write property test for video URL resolution (Property 9)
    - **Property 9: Video URL resolution**
    - **Validates: Requirements 8.5**

- [x] 3. Implement shared UI components
  - [x] 3.1 Create `mobile/components/AppHeader.tsx`
    - Gradient icon + "TikTok AI" styled text
    - Optional `title` prop for subtitle
    - _Requirements: 7.6_

  - [x] 3.2 Create `mobile/components/ProgressBar.tsx`
    - Accept `progress` (0–100) and `message` props
    - Use `expo-linear-gradient` with `#fe2c55 → #25f4ee`
    - Display percentage and message text
    - _Requirements: 4.2, 4.3_

  - [ ]* 3.3 Write property test for ProgressBar (Property 4)
    - **Property 4: Progress bar renders any progress value**
    - **Validates: Requirements 4.2**

  - [x] 3.4 Create `mobile/components/VideoPlayer.tsx`
    - Wrap `expo-av` Video with `useNativeControls`
    - Rounded container (borderRadius 12), black background
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 3.5 Create `mobile/components/FormSelector.tsx`
    - Native Picker wrapped in styled container
    - Border `#2a2a2a`, background `#1a1a1a`
    - _Requirements: 3.2, 3.3, 3.6_

  - [x] 3.6 Create `mobile/components/ToggleGroup.tsx`
    - Render toggle buttons with active/inactive styles
    - Accept `activeColor` and `activeTextColor` props
    - _Requirements: 3.4, 3.5_

  - [x] 3.7 Create `mobile/components/VideoCard.tsx`
    - Embed VideoPlayer, show filename and size in MB
    - Download, share, and delete action buttons
    - _Requirements: 6.4, 6.5, 6.9_

  - [ ]* 3.8 Write property test for VideoCard (Property 6)
    - **Property 6: Video card renders all required fields**
    - **Validates: Requirements 6.4**

- [x] 4. Checkpoint — Ensure all component tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement navigation layouts
  - [x] 5.1 Create `mobile/app/_layout.tsx` (root Stack layout + StatusBar)
    - Configure Stack with dark background
    - Set StatusBar style to light
    - _Requirements: 1.2, 7.1_

  - [x] 5.2 Create `mobile/app/(tabs)/_layout.tsx` (Tab bar layout)
    - Two tabs: "Crear" (index) and "Biblioteca" (library)
    - Active color `#fe2c55`, inactive `#555555`
    - Background `#010101`, top border `#1a1a1a`
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [ ]* 5.3 Write property test for tab active/inactive coloring (Property 1)
    - **Property 1: Tab active/inactive coloring**
    - **Validates: Requirements 2.3, 2.4**

- [x] 6. Implement GenerateScreen
  - [x] 6.1 Create `mobile/app/(tabs)/index.tsx` with form state and UI
    - Topic TextInput (maxLength 200), FormSelector for style/niche/voice
    - ToggleGroup for duration and language
    - Switch for subtitles
    - Disable submit button when topic is empty/whitespace
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

  - [x] 6.2 Wire form submission and polling logic
    - POST to `/api/generate` on submit, store `job_id`
    - Start Poller (setInterval 2000ms) using `useRef` for cleanup
    - Update ProgressBar while status is `pending`/`running`
    - Stop poller and show VideoPlayer on `completed`
    - Stop poller and show error on `error` or network failure
    - _Requirements: 3.9, 3.10, 4.1, 4.2, 4.4, 4.5, 4.6, 4.7_

  - [x] 6.3 Add download and share actions
    - "Descargar MP4" button using `expo-file-system`
    - "Compartir" button using `expo-sharing`
    - _Requirements: 5.4, 5.5, 5.6, 5.7_

  - [ ]* 6.4 Write property test for empty/whitespace topic disables submit (Property 2)
    - **Property 2: Empty/whitespace topic disables submit**
    - **Validates: Requirements 3.8**

  - [ ]* 6.5 Write property test for form submission payload completeness (Property 3)
    - **Property 3: Form submission payload completeness**
    - **Validates: Requirements 3.9**

  - [ ]* 6.6 Write property test for poller cleanup on unmount (Property 5)
    - **Property 5: Poller cleanup on unmount**
    - **Validates: Requirements 4.7**

- [x] 7. Implement LibraryScreen
  - [x] 7.1 Create `mobile/app/(tabs)/library.tsx` with video list and state
    - Fetch `/api/videos` on mount, show loading spinner
    - Empty-state message when list is empty
    - Render VideoCard for each video
    - Refresh button to re-fetch list
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 7.2 Add delete confirmation and share logic
    - Confirmation modal before delete
    - DELETE request on confirm, remove from list without full reload
    - Share button via `expo-sharing`
    - Error alert on DELETE failure
    - _Requirements: 6.6, 6.7, 6.8, 6.9_

  - [ ]* 7.3 Write property test for delete removes video from list (Property 7)
    - **Property 7: Delete removes video from list**
    - **Validates: Requirements 6.7**

- [-] 8. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (using fast-check)
- Unit tests validate specific examples and edge cases (using jest-expo + @testing-library/react-native)
