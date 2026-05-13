import * as FileSystem from 'expo-file-system'
import * as Sharing from 'expo-sharing'
import { Alert, Pressable, StyleSheet, Text, View } from 'react-native'
import { VideoItem, getVideoUrl } from '../lib/api'
import { COLORS } from '../lib/constants'
import VideoPlayer from './VideoPlayer'

interface VideoCardProps {
  video: VideoItem
  onDelete: (filename: string) => void
  onShare: (filename: string) => void
}

export default function VideoCard({ video, onDelete, onShare }: VideoCardProps) {
  const resolvedUrl = getVideoUrl(video.url)

  async function handleDownload() {
    try {
      const dest = FileSystem.documentDirectory + video.filename
      await FileSystem.downloadAsync(resolvedUrl, dest)
      Alert.alert('Descarga completa', `Video guardado en el dispositivo.`)
    } catch {
      Alert.alert('Error', 'Error al descargar el video')
    }
  }

  async function handleShare() {
    try {
      const isAvailable = await Sharing.isAvailableAsync()
      if (!isAvailable) {
        Alert.alert('No disponible', 'Compartir no está disponible en este dispositivo.')
        return
      }
      const dest = FileSystem.cacheDirectory + video.filename
      await FileSystem.downloadAsync(resolvedUrl, dest)
      await Sharing.shareAsync(dest)
    } catch {
      onShare(video.filename)
    }
  }

  return (
    <View style={styles.card}>
      <VideoPlayer uri={resolvedUrl} style={styles.player} />
      <View style={styles.info}>
        <Text style={styles.filename} numberOfLines={1}>
          {video.filename}
        </Text>
        <Text style={styles.size}>{video.size_mb.toFixed(2)} MB</Text>
      </View>
      <View style={styles.actions}>
        <Pressable style={[styles.btn, styles.btnDownload]} onPress={handleDownload}>
          <Text style={styles.btnText}>⬇ Descargar</Text>
        </Pressable>
        <Pressable style={[styles.btn, styles.btnShare]} onPress={handleShare}>
          <Text style={styles.btnText}>↗ Compartir</Text>
        </Pressable>
        <Pressable
          style={[styles.btn, styles.btnDelete]}
          onPress={() => onDelete(video.filename)}
        >
          <Text style={styles.btnText}>🗑</Text>
        </Pressable>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: COLORS.cardBg,
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 16,
  },
  player: {
    borderRadius: 0,
  },
  info: {
    paddingHorizontal: 12,
    paddingTop: 10,
    gap: 2,
  },
  filename: {
    color: COLORS.textPrimary,
    fontSize: 14,
    fontWeight: '500',
  },
  size: {
    color: COLORS.textSecondary,
    fontSize: 12,
  },
  actions: {
    flexDirection: 'row',
    gap: 8,
    padding: 12,
  },
  btn: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnDownload: {
    backgroundColor: COLORS.primary,
  },
  btnShare: {
    backgroundColor: COLORS.cardBg,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  btnDelete: {
    backgroundColor: COLORS.cardBg,
    borderWidth: 1,
    borderColor: COLORS.border,
    flex: 0,
    paddingHorizontal: 14,
  },
  btnText: {
    color: COLORS.textPrimary,
    fontSize: 13,
    fontWeight: '600',
  },
})
