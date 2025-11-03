# Guía Completa: Base de Datos Spotify (8M+ Tracks)

## 📋 Información General

**Dataset**: 8+ Million Spotify Tracks, Genre, Audio Features  
**Fuente**: [Kaggle - maltegrosse](https://www.kaggle.com/datasets/maltegrosse/8-m-spotify-tracks-genre-audio-features/data)  
**Tamaño**: ~5GB  
**Formato**: SQLite (.sqlite)  
**Tipo de datos**: BLOB (requiere casting a VARCHAR/INT/FLOAT)

---

## 🗂️ Estructura de la Base de Datos

### Resumen de Tablas

| Tabla | Descripción | Registros Aprox. |
|-------|-------------|------------------|
| `tracks` | Información de canciones | 8M+ |
| `artists` | Información de artistas | ~1M |
| `albums` | Información de álbumes | ~2M |
| `genres` | Lista de géneros musicales | ~5000 |
| `audio_features` | Características de audio Spotify | 8M+ |
| `r_track_artist` | Relación tracks ↔ artists | 10M+ |
| `r_albums_tracks` | Relación albums ↔ tracks | 10M+ |
| `r_albums_artists` | Relación albums ↔ artists | 3M+ |
| `r_artist_genre` | Relación artists ↔ genres | 2M+ |

---

## 📊 Tablas Principales

### 1. `tracks` - Canciones

Contiene la información principal de cada canción.

**Columnas:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | BLOB | ID único de la canción (Spotify ID) |
| `name` | BLOB | Nombre de la canción |
| `disc_number` | BLOB | Número de disco |
| `duration` | BLOB | Duración en milisegundos |
| `explicit` | BLOB | Si tiene contenido explícito (0/1) |
| `audio_feature_id` | BLOB | ID relacionado con audio_features |
| `preview_url` | BLOB | URL de preview de 30s |
| `track_number` | BLOB | Número de track en el álbum |
| `popularity` | BLOB | Popularidad (0-100) |
| `is_playable` | BLOB | Si está disponible para reproducir |

**Ejemplo de consulta:**
```sql
SELECT 
    CAST(name AS VARCHAR) as cancion,
    CAST(popularity AS VARCHAR)::INT as popularidad,
    CAST(duration AS VARCHAR)::INT as duracion_ms
FROM tracks
WHERE CAST(popularity AS VARCHAR)::INT > 80
LIMIT 10;
```

---

### 2. `artists` - Artistas

Información sobre los artistas musicales.

**Columnas:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | BLOB | ID único del artista (Spotify ID) |
| `name` | BLOB | Nombre del artista |
| `popularity` | BLOB | Popularidad del artista (0-100) |
| `followers` | BLOB | Número de seguidores |

**Ejemplo de consulta:**
```sql
SELECT 
    CAST(name AS VARCHAR) as artista,
    CAST(popularity AS VARCHAR)::INT as popularidad,
    CAST(followers AS VARCHAR)::INT as seguidores
FROM artists
ORDER BY CAST(followers AS VARCHAR)::INT DESC
LIMIT 10;
```

---

### 3. `albums` - Álbumes

Información de álbumes y singles.

**Columnas:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | BLOB | ID único del álbum |
| `name` | BLOB | Nombre del álbum |
| `album_group` | BLOB | Tipo de grupo del álbum |
| `album_type` | BLOB | Tipo: "album", "single", "compilation" |
| `release_date` | BLOB | Fecha de lanzamiento (timestamp) |
| `popularity` | BLOB | Popularidad del álbum (0-100) |

**Ejemplo de consulta:**
```sql
SELECT 
    CAST(name AS VARCHAR) as album,
    CAST(album_type AS VARCHAR) as tipo,
    CAST(popularity AS VARCHAR)::INT as popularidad
FROM albums
WHERE CAST(album_type AS VARCHAR) = 'album'
LIMIT 10;
```

---

### 4. `genres` - Géneros

Lista de géneros musicales disponibles.

**Columnas:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | BLOB | Nombre del género (funciona como ID y nombre) |

**Géneros disponibles (ejemplos):**
- Hip Hop: `detroit hip hop`, `east coast hip hop`, `gangster rap`, `conscious hip hop`
- Rock: `rock`, `alternative rock`, `indie rock`, `punk rock`
- Electronic: `electro`, `techno`, `house`, `edm`
- Pop: `pop`, `k-pop`, `j-pop`, `indie pop`
- Rap: `rap`, `trap`, `pop rap`, `cali rap`

**Ejemplo de consulta:**
```sql
SELECT CAST(id AS VARCHAR) as genero
FROM genres
WHERE CAST(id AS VARCHAR) LIKE '%rock%'
ORDER BY genero;
```

---

### 5. `audio_features` - Características de Audio

Características musicales y de audio proporcionadas por Spotify.

**Columnas:**

| Campo | Tipo | Rango | Descripción |
|-------|------|-------|-------------|
| `id` | BLOB | - | ID de la canción |
| `acousticness` | BLOB | 0.0-1.0 | Nivel de acústico |
| `danceability` | BLOB | 0.0-1.0 | Qué tan bailable es |
| `energy` | BLOB | 0.0-1.0 | Intensidad y actividad |
| `instrumentalness` | BLOB | 0.0-1.0 | Contenido instrumental (sin voz) |
| `key` | BLOB | 0-11 | Tonalidad musical |
| `liveness` | BLOB | 0.0-1.0 | Presencia de audiencia en vivo |
| `loudness` | BLOB | -60-0 dB | Volumen general |
| `mode` | BLOB | 0/1 | Modalidad (0=menor, 1=mayor) |
| `speechiness` | BLOB | 0.0-1.0 | Presencia de palabras habladas |
| `tempo` | BLOB | BPM | Tempo en beats por minuto |
| `time_signature` | BLOB | 3-7 | Compás |
| `valence` | BLOB | 0.0-1.0 | Positividad musical (feliz/triste) |
| `duration` | BLOB | ms | Duración en milisegundos |
| `analysis_url` | BLOB | - | URL de análisis de Spotify |

**Interpretación de métricas clave:**

- **Energy** (0.0-1.0): 
  - 0.0-0.3: Calmada, relajada
  - 0.7-1.0: Enérgica, intensa

- **Danceability** (0.0-1.0):
  - 0.0-0.4: Poco bailable
  - 0.7-1.0: Muy bailable

- **Valence** (0.0-1.0):
  - 0.0-0.3: Triste, melancólica
  - 0.7-1.0: Alegre, positiva

- **Tempo**: BPM típicos
  - 60-90: Lento (baladas)
  - 120-140: Medio (pop, rock)
  - 140+: Rápido (EDM, metal)

**Ejemplo de consulta:**
```sql
SELECT 
    CAST(id AS VARCHAR) as track_id,
    CAST(energy AS VARCHAR)::FLOAT as energia,
    CAST(danceability AS VARCHAR)::FLOAT as bailabilidad,
    CAST(valence AS VARCHAR)::FLOAT as positividad,
    CAST(tempo AS VARCHAR)::FLOAT as tempo
FROM audio_features
WHERE CAST(energy AS VARCHAR)::FLOAT > 0.8
  AND CAST(danceability AS VARCHAR)::FLOAT > 0.7
LIMIT 10;
```

---

## 🔗 Tablas de Relación

### 6. `r_track_artist` - Relación Tracks ↔ Artists

Relaciona canciones con artistas (muchos a muchos).

**Columnas:**
- `track_id`: ID de la canción
- `artist_id`: ID del artista

---

### 7. `r_albums_tracks` - Relación Albums ↔ Tracks

Relaciona álbumes con canciones.

**Columnas:**
- `album_id`: ID del álbum
- `track_id`: ID de la canción

---

### 8. `r_albums_artists` - Relación Albums ↔ Artists

Relaciona álbumes con artistas.

**Columnas:**
- `album_id`: ID del álbum
- `artist_id`: ID del artista

---

### 9. `r_artist_genre` - Relación Artists ↔ Genres

Relaciona artistas con géneros musicales.

**Columnas:**
- `artist_id`: ID del artista
- `genre_id`: ID del género

---

## 🔍 Consultas Útiles

### Consulta Completa: Canciones con toda la información

```sql
SELECT 
    CAST(t.name AS VARCHAR) as cancion,
    CAST(a.name AS VARCHAR) as artista,
    CAST(al.name AS VARCHAR) as album,
    CAST(g.id AS VARCHAR) as genero,
    CAST(t.popularity AS VARCHAR)::INT as popularidad,
    CAST(af.energy AS VARCHAR)::FLOAT as energia,
    CAST(af.danceability AS VARCHAR)::FLOAT as bailabilidad,
    CAST(af.valence AS VARCHAR)::FLOAT as positividad,
    CAST(af.tempo AS VARCHAR)::FLOAT as tempo
FROM tracks t
JOIN r_track_artist rta ON t.id = rta.track_id
JOIN artists a ON rta.artist_id = a.id
JOIN r_artist_genre rag ON a.id = rag.artist_id
JOIN genres g ON rag.genre_id = g.id
JOIN audio_features af ON t.audio_feature_id = af.id
JOIN r_albums_tracks rat ON t.id = rat.track_id
JOIN albums al ON rat.album_id = al.id
LIMIT 100;
```

### Filtrar por Género

```sql
SELECT 
    CAST(t.name AS VARCHAR) as cancion,
    CAST(a.name AS VARCHAR) as artista,
    CAST(t.popularity AS VARCHAR)::INT as popularidad
FROM tracks t
JOIN r_track_artist rta ON t.id = rta.track_id
JOIN artists a ON rta.artist_id = a.id
JOIN r_artist_genre rag ON a.id = rag.artist_id
JOIN genres g ON rag.genre_id = g.id
WHERE CAST(g.id AS VARCHAR) LIKE '%rock%'
  AND CAST(t.popularity AS VARCHAR)::INT > 50
ORDER BY CAST(t.popularity AS VARCHAR)::INT DESC
LIMIT 20;
```

### Top Artistas por Género

```sql
SELECT 
    CAST(a.name AS VARCHAR) as artista,
    CAST(g.id AS VARCHAR) as genero,
    CAST(a.popularity AS VARCHAR)::INT as popularidad,
    CAST(a.followers AS VARCHAR)::INT as seguidores
FROM artists a
JOIN r_artist_genre rag ON a.id = rag.artist_id
JOIN genres g ON rag.genre_id = g.id
WHERE CAST(g.id AS VARCHAR) = 'hip hop'
ORDER BY CAST(a.popularity AS VARCHAR)::INT DESC
LIMIT 10;
```

### Canciones para Entrenar (Alta energía + bailables)

```sql
SELECT 
    CAST(t.name AS VARCHAR) as cancion,
    CAST(a.name AS VARCHAR) as artista,
    CAST(af.energy AS VARCHAR)::FLOAT as energia,
    CAST(af.danceability AS VARCHAR)::FLOAT as bailabilidad,
    CAST(af.tempo AS VARCHAR)::FLOAT as tempo
FROM tracks t
JOIN r_track_artist rta ON t.id = rta.track_id
JOIN artists a ON rta.artist_id = a.id
JOIN audio_features af ON t.audio_feature_id = af.id
WHERE CAST(af.energy AS VARCHAR)::FLOAT > 0.8
  AND CAST(af.danceability AS VARCHAR)::FLOAT > 0.7
  AND CAST(af.tempo AS VARCHAR)::FLOAT > 120
  AND CAST(t.popularity AS VARCHAR)::INT > 40
ORDER BY CAST(t.popularity AS VARCHAR)::INT DESC
LIMIT 30;
```

### Canciones Relajantes (Acústicas + lentas)

```sql
SELECT 
    CAST(t.name AS VARCHAR) as cancion,
    CAST(a.name AS VARCHAR) as artista,
    CAST(af.acousticness AS VARCHAR)::FLOAT as acustico,
    CAST(af.energy AS VARCHAR)::FLOAT as energia,
    CAST(af.tempo AS VARCHAR)::FLOAT as tempo
FROM tracks t
JOIN r_track_artist rta ON t.id = rta.track_id
JOIN artists a ON rta.artist_id = a.id
JOIN audio_features af ON t.audio_feature_id = af.id
WHERE CAST(af.acousticness AS VARCHAR)::FLOAT > 0.6
  AND CAST(af.energy AS VARCHAR)::FLOAT < 0.4
  AND CAST(af.tempo AS VARCHAR)::FLOAT < 100
  AND CAST(t.popularity AS VARCHAR)::INT > 30
LIMIT 30;
```

### Estadísticas por Género

```sql
SELECT 
    CAST(g.id AS VARCHAR) as genero,
    COUNT(DISTINCT t.id) as total_canciones,
    AVG(CAST(af.energy AS VARCHAR)::FLOAT) as energia_promedio,
    AVG(CAST(af.danceability AS VARCHAR)::FLOAT) as bailabilidad_promedio,
    AVG(CAST(af.valence AS VARCHAR)::FLOAT) as positividad_promedio,
    AVG(CAST(af.tempo AS VARCHAR)::FLOAT) as tempo_promedio
FROM tracks t
JOIN r_track_artist rta ON t.id = rta.track_id
JOIN r_artist_genre rag ON rta.artist_id = rag.artist_id
JOIN genres g ON rag.genre_id = g.id
JOIN audio_features af ON t.audio_feature_id = af.id
GROUP BY g.id
ORDER BY total_canciones DESC
LIMIT 20;
```

---

## 💡 Casos de Uso para Agentes

### 1. Sistema de Recomendaciones por Mood

**Moods sugeridos:**
- **Happy**: `valence > 0.7 AND danceability > 0.6`
- **Sad**: `valence < 0.3 AND tempo < 100`
- **Energetic**: `energy > 0.8 AND tempo > 120`
- **Chill**: `tempo < 100 AND acousticness > 0.5`
- **Party**: `danceability > 0.7 AND energy > 0.7`
- **Focus**: `instrumentalness > 0.5 AND energy < 0.5`

### 2. Búsqueda Semántica

El agente puede interpretar descripciones naturales:
- "Música para correr" → alta energía + tempo rápido
- "Canciones tristes de rock" → rock + baja valencia
- "Lo más popular de trap" → trap + popularidad > 70

### 3. Análisis de Tendencias

- Comparar características de audio entre géneros
- Identificar artistas emergentes (followers bajo, popularidad alta)
- Encontrar géneros similares por características de audio

### 4. Playlist Inteligente

Crear playlists basadas en:
- Transiciones suaves de energía
- Similitud de tempo
- Coherencia de género

---

## ⚠️ Consideraciones Importantes

### Manejo de BLOB

**Todos los datos están en formato BLOB y requieren casting:**

```sql
-- ❌ Incorrecto
SELECT name FROM tracks WHERE popularity > 50

-- ✅ Correcto
SELECT CAST(name AS VARCHAR) as cancion 
FROM tracks 
WHERE CAST(popularity AS VARCHAR)::INT > 50
```

### Tipos de Casting

| Tipo SQL | Uso |
|----------|-----|
| `CAST(campo AS VARCHAR)` | Para texto (nombres, IDs) |
| `CAST(campo AS VARCHAR)::INT` | Para números enteros |
| `CAST(campo AS VARCHAR)::FLOAT` | Para decimales |

### Tamaño del Dataset

- **Total**: ~8M canciones
- Para agentes, considera:
  - Muestra de 50-100 canciones por género (~100-200MB)
  - Filtrar por `popularity > 30` para datos relevantes
  - Usar estadísticas agregadas en vez de datos individuales

---

## 🚀 Código Python de Conexión

```python
import duckdb

# Conectar a la base de datos
conn = duckdb.connect('spotify.sqlite')

# Función helper para consultas
def query(sql):
    return conn.execute(sql).df()

# Ejemplo de uso
df = query("""
    SELECT 
        CAST(t.name AS VARCHAR) as cancion,
        CAST(a.name AS VARCHAR) as artista
    FROM tracks t
    JOIN r_track_artist rta ON t.id = rta.track_id
    JOIN artists a ON rta.artist_id = a.id
    LIMIT 10
""")

print(df)
```

---

## 📚 Recursos Adicionales

- **Dataset original**: [Kaggle Link](https://www.kaggle.com/datasets/maltegrosse/8-m-spotify-tracks-genre-audio-features/data)
- **Spotify Audio Features**: [Documentación oficial](https://developer.spotify.com/documentation/web-api/reference/get-audio-features)
- **DuckDB**: [Documentación](https://duckdb.org/docs/)

---

## 📝 Glosario Rápido

| Término | Definición |
|---------|------------|
| **Track** | Canción individual |
| **Album** | Colección de canciones (álbum o single) |
| **Artist** | Intérprete o banda |
| **Genre** | Género musical |
| **Audio Features** | Características musicales medibles por Spotify |
| **Popularity** | Métrica 0-100 basada en streams y recencia |
| **Valence** | Positividad/negatividad musical |
| **Tempo** | Velocidad de la canción en BPM |
| **Energy** | Intensidad y actividad de la canción |
| **Danceability** | Qué tan adecuada es para bailar |

---

**Última actualización**: Noviembre 2025  
**Versión**: 1.0
