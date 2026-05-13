import { useCallback, useState } from 'react'
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Modal,
  Pressable,
  RefreshControl,
  StyleSheet,
  Text,
  View,
} from 'react-native'
import { useFocusEffect } from 'expo-router'
import AppHeader from '../../components/AppHeader'
import VideoCard from '../../components/VideoCard'
import { VideoItem, deleteVideo, listVideos } from '../../lib/api'
import { COLORS } from '../../lib/constants'

export default function LibraryScreen() {
  const [videos, setVideos] = useState<VideoItem[]>([])
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null)
  const [deleting, setDeleting] = useState<string | null>(null)

  async function fetchVideos(isRefresh = false) {
    if (isRefresh) setRefreshing(true)
    else setLoading(true)
    setError(null)
    try {
      const data = await listVideos()
      setVideos(data.videos)
    } catch (e: unknown) {
      setError(
        e instanceof Error ? e.message : 'Error al cargar los videos'
      )
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  // Reload when tab gains focus
  useFocusEffect(
    useCallback(() => {
      fetchVideos()
    }, [])
  )

  async function handleConfirmDelete() {
    if (!confirmDelete) return
    setDeleting(confirmDelete)
    setConfirmDelete(null)
    try {
      await deleteVideo(confirmDelete)
      setVideos((prev) => prev.filter((v) => v.filename !== confirmDelete))
    } catch {
      Alert.alert('Error', 'Error al eliminar el video')
    } finally {
      setDeleting(null)
    }
  }

  function handleShare(filename: string) {
    // Fallback: share by filename (VideoCard handles the actual sharing)
    Alert.alert('Compartir', `Compartiendo: ${filename}`)
  }

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    )
  }

  return (
    <View style={styles.container}>
      <AppHeader />

      {/* Header row */}
      <View style={styles.headerRow}>
        <Text style={styles.title}>Mis Videos</Text>
        <Pressable style={styles.refreshBtn} onPress={() => fetchVideos(true)}>
          <Text style={styles.refreshText}>↻ Actualizar</Text>
        </Pressable>
      </View>

      {error ? (
        <View style={styles.centered}>
          <Text style={styles.errorText}>{error}</Text>
          <Pressable style={styles.retryBtn} onPress={() => fetchVideos()}>
            <Text style={styles.retryText}>Reintentar</Text>
          </Pressable>
        </View>
      ) : (
        <FlatList
          data={videos}
          keyExtractor={(item) => item.filename}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={() => fetchVideos(true)}
              tintColor={COLORS.primary}
            />
          }
          ListEmptyComponent={
            <View style={styles.emptyState}>
              <Text style={styles.emptyIcon}>🎬</Text>
              <Text style={styles.emptyText}>
                No hay videos aún. Genera tu primer video en la pestaña Crear.
              </Text>
            </View>
          }
          renderItem={({ item }) => (
            <View style={deleting === item.filename ? styles.deleting : undefined}>
              <VideoCard
                video={item}
                onDelete={(filename) => setConfirmDelete(filename)}
                onShare={handleShare}
              />
            </View>
          )}
        />
      )}

      {/* Delete confirmation modal */}
      <Modal
        visible={confirmDelete !== null}
        transparent
        animationType="fade"
        onRequestClose={() => setConfirmDelete(null)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalBox}>
            <Text style={styles.modalTitle}>Eliminar video</Text>
            <Text style={styles.modalMessage}>
              ¿Estás seguro de que quieres eliminar este video? Esta acción no se puede deshacer.
            </Text>
            <View style={styles.modalActions}>
              <Pressable
                style={[styles.modalBtn, styles.modalBtnCancel]}
                onPress={() => setConfirmDelete(null)}
              >
                <Text style={styles.modalBtnText}>Cancelar</Text>
              </Pressable>
              <Pressable
                style={[styles.modalBtn, styles.modalBtnDelete]}
                onPress={handleConfirmDelete}
              >
                <Text style={styles.modalBtnText}>Eliminar</Text>
              </Pressable>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  centered: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    padding: 16,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  title: {
    color: COLORS.textPrimary,
    fontSize: 18,
    fontWeight: '700',
  },
  refreshBtn: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: COLORS.cardBg,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  refreshText: {
    color: COLORS.textSecondary,
    fontSize: 13,
  },
  list: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  emptyState: {
    alignItems: 'center',
    paddingTop: 60,
    gap: 12,
  },
  emptyIcon: {
    fontSize: 48,
  },
  emptyText: {
    color: COLORS.textSecondary,
    fontSize: 15,
    textAlign: 'center',
    lineHeight: 22,
  },
  errorText: {
    color: '#ff6b6b',
    fontSize: 14,
    textAlign: 'center',
  },
  retryBtn: {
    backgroundColor: COLORS.primary,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 10,
  },
  retryText: {
    color: COLORS.textPrimary,
    fontWeight: '600',
  },
  deleting: {
    opacity: 0.4,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  modalBox: {
    backgroundColor: COLORS.cardBg,
    borderRadius: 16,
    padding: 24,
    width: '100%',
    gap: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  modalTitle: {
    color: COLORS.textPrimary,
    fontSize: 17,
    fontWeight: '700',
  },
  modalMessage: {
    color: COLORS.textSecondary,
    fontSize: 14,
    lineHeight: 20,
  },
  modalActions: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 4,
  },
  modalBtn: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  modalBtnCancel: {
    backgroundColor: COLORS.background,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  modalBtnDelete: {
    backgroundColor: COLORS.primary,
  },
  modalBtnText: {
    color: COLORS.textPrimary,
    fontWeight: '600',
    fontSize: 14,
  },
})
