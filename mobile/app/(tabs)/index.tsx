import * as FileSystem from 'expo-file-system'
import * as Sharing from 'expo-sharing'
import { useEffect, useRef, useState } from 'react'
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from 'react-native'
import AppHeader from '../../components/AppHeader'
import FormSelector from '../../components/FormSelector'
import ProgressBar from '../../components/ProgressBar'
import ToggleGroup from '../../components/ToggleGroup'
import VideoPlayer from '../../components/VideoPlayer'
import {
  JobStatus,
  generateVideo,
  getJobStatus,
  getVideoUrl,
} from '../../lib/api'
import {
  COLORS,
  DURATION_OPTIONS,
  NICHE_OPTIONS,
  STYLES_OPTIONS,
  VOICE_OPTIONS,
} from '../../lib/constants'

interface FormState {
  topic: string
  style: string
  audience: string
  duration: number
  language: string
  voice: string
  add_subtitles: boolean
  niche: string
}

const DEFAULT_FORM: FormState = {
  topic: '',
  style: 'entretenido',
  audience: 'general',
  duration: 30,
  language: 'es',
  voice: 'edge',
  add_subtitles: true,
  niche: 'general',
}

export default function GenerateScreen() {
  const [form, setForm] = useState<FormState>(DEFAULT_FORM)
  const [jobId, setJobId] = useState<string | null>(null)
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Cleanup poller on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [])

  // Start/stop poller based on jobId
  useEffect(() => {
    if (!jobId) return

    const poll = async () => {
      try {
        const status = await getJobStatus(jobId)
        setJobStatus(status)
        if (status.status === 'completed' || status.status === 'error') {
          if (pollRef.current) clearInterval(pollRef.current)
          pollRef.current = null
          setLoading(false)
        }
      } catch {
        if (pollRef.current) clearInterval(pollRef.current)
        pollRef.current = null
        setLoading(false)
        setError('Error al consultar el estado del video')
      }
    }

    pollRef.current = setInterval(poll, 2000)
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [jobId])

  function setField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const isTopicEmpty = form.topic.trim().length === 0

  async function handleSubmit() {
    if (isTopicEmpty) return
    setError(null)
    setJobStatus(null)
    setJobId(null)
    setLoading(true)
    try {
      const { job_id } = await generateVideo(form)
      setJobId(job_id)
    } catch (e: unknown) {
      setLoading(false)
      setError(
        e instanceof Error ? e.message : 'Error al iniciar la generación'
      )
    }
  }

  async function handleDownload() {
    if (!jobStatus?.video_url) return
    try {
      const url = getVideoUrl(jobStatus.video_url)
      const filename = url.split('/').pop() ?? 'video.mp4'
      const dest = FileSystem.documentDirectory + filename
      await FileSystem.downloadAsync(url, dest)
      Alert.alert('Descarga completa', 'Video guardado en el dispositivo.')
    } catch {
      Alert.alert('Error', 'Error al descargar el video')
    }
  }

  async function handleShare() {
    if (!jobStatus?.video_url) return
    try {
      const isAvailable = await Sharing.isAvailableAsync()
      if (!isAvailable) return
      const url = getVideoUrl(jobStatus.video_url)
      const filename = url.split('/').pop() ?? 'video.mp4'
      const dest = FileSystem.cacheDirectory + filename
      await FileSystem.downloadAsync(url, dest)
      await Sharing.shareAsync(dest)
    } catch {
      Alert.alert('Error', 'No se pudo compartir el video')
    }
  }

  const isPolling =
    loading &&
    jobStatus?.status !== 'completed' &&
    jobStatus?.status !== 'error'

  const videoUrl =
    jobStatus?.status === 'completed' && jobStatus.video_url
      ? getVideoUrl(jobStatus.video_url)
      : null

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <AppHeader />
      <ScrollView
        style={styles.flex}
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
      >
        {/* Topic */}
        <View style={styles.field}>
          <Text style={styles.label}>Tema del video</Text>
          <TextInput
            style={styles.input}
            placeholder="Ej: Los beneficios del ayuno intermitente"
            placeholderTextColor={COLORS.textSecondary}
            value={form.topic}
            onChangeText={(v) => setField('topic', v)}
            maxLength={200}
            multiline
          />
          <Text style={styles.charCount}>{form.topic.length}/200</Text>
        </View>

        {/* Style */}
        <View style={styles.field}>
          <FormSelector
            label="Estilo"
            value={form.style}
            options={STYLES_OPTIONS}
            onChange={(v) => setField('style', v)}
          />
        </View>

        {/* Niche */}
        <View style={styles.field}>
          <FormSelector
            label="Nicho"
            value={form.niche}
            options={NICHE_OPTIONS}
            onChange={(v) => setField('niche', v)}
          />
        </View>

        {/* Duration */}
        <View style={styles.field}>
          <Text style={styles.label}>Duración</Text>
          <ToggleGroup
            options={DURATION_OPTIONS}
            value={form.duration}
            onChange={(v) => setField('duration', Number(v))}
            activeColor={COLORS.primary}
          />
        </View>

        {/* Language */}
        <View style={styles.field}>
          <Text style={styles.label}>Idioma</Text>
          <ToggleGroup
            options={[
              { value: 'es', label: 'ES' },
              { value: 'en', label: 'EN' },
            ]}
            value={form.language}
            onChange={(v) => setField('language', String(v))}
            activeColor={COLORS.secondary}
            activeTextColor="#000000"
          />
        </View>

        {/* Voice */}
        <View style={styles.field}>
          <FormSelector
            label="Voz"
            value={form.voice}
            options={VOICE_OPTIONS}
            onChange={(v) => setField('voice', v)}
          />
        </View>

        {/* Subtitles */}
        <View style={styles.switchRow}>
          <Text style={styles.label}>Agregar subtítulos</Text>
          <Switch
            value={form.add_subtitles}
            onValueChange={(v) => setField('add_subtitles', v)}
            trackColor={{ false: COLORS.border, true: COLORS.primary }}
            thumbColor={COLORS.textPrimary}
          />
        </View>

        {/* Error */}
        {error ? <Text style={styles.errorText}>{error}</Text> : null}

        {/* Submit */}
        <Pressable
          style={[styles.submitBtn, isTopicEmpty && styles.submitBtnDisabled]}
          onPress={handleSubmit}
          disabled={isTopicEmpty || loading}
        >
          <Text style={styles.submitText}>
            {loading ? 'Generando...' : '✨ Generar Video'}
          </Text>
        </Pressable>

        {/* Progress */}
        {isPolling && jobStatus ? (
          <View style={styles.progressSection}>
            <ProgressBar
              progress={jobStatus.progress}
              message={jobStatus.message}
            />
          </View>
        ) : null}

        {/* Job error */}
        {jobStatus?.status === 'error' ? (
          <Text style={styles.errorText}>{jobStatus.message}</Text>
        ) : null}

        {/* Video result */}
        {videoUrl ? (
          <View style={styles.resultSection}>
            <VideoPlayer uri={videoUrl} />
            <View style={styles.resultActions}>
              <Pressable style={styles.actionBtn} onPress={handleDownload}>
                <Text style={styles.actionBtnText}>⬇ Descargar MP4</Text>
              </Pressable>
              <Pressable
                style={[styles.actionBtn, styles.actionBtnSecondary]}
                onPress={handleShare}
              >
                <Text style={styles.actionBtnText}>↗ Compartir</Text>
              </Pressable>
            </View>
          </View>
        ) : null}
      </ScrollView>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: COLORS.background },
  content: {
    padding: 16,
    gap: 16,
    paddingBottom: 40,
  },
  field: { gap: 6 },
  label: {
    color: COLORS.textSecondary,
    fontSize: 13,
    fontWeight: '500',
  },
  input: {
    backgroundColor: COLORS.cardBg,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 12,
    padding: 12,
    color: COLORS.textPrimary,
    fontSize: 15,
    minHeight: 80,
    textAlignVertical: 'top',
  },
  charCount: {
    color: COLORS.textSecondary,
    fontSize: 11,
    textAlign: 'right',
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  submitBtn: {
    backgroundColor: COLORS.primary,
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: 'center',
  },
  submitBtnDisabled: {
    opacity: 0.4,
  },
  submitText: {
    color: COLORS.textPrimary,
    fontSize: 16,
    fontWeight: '700',
  },
  errorText: {
    color: '#ff6b6b',
    fontSize: 13,
    textAlign: 'center',
  },
  progressSection: {
    gap: 8,
  },
  resultSection: {
    gap: 12,
  },
  resultActions: {
    flexDirection: 'row',
    gap: 10,
  },
  actionBtn: {
    flex: 1,
    backgroundColor: COLORS.primary,
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
  },
  actionBtnSecondary: {
    backgroundColor: COLORS.cardBg,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  actionBtnText: {
    color: COLORS.textPrimary,
    fontSize: 14,
    fontWeight: '600',
  },
})
