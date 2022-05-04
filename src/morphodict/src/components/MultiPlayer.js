import React, { useState, useEffect } from 'react'

// https://stackoverflow.com/questions/47686345/playing-sound-in-react-js

const useMultiAudio = recordings => {
  const [sources] = useState(
    recordings.map(rec => {
      const rec_url = rec.recording_url;
      const speaker = rec.speaker_name;
      const language = rec.language[0]
      return {
        rec_url,
        audio: new Audio(rec_url),
        speaker,
        language
      }
    }),
  )

  const [players, setPlayers] = useState(
    recordings.map(url => {
      return {
        url,
        playing: false,
      }
    }),
  )

  const toggle = targetIndex => () => {
    const newPlayers = [...players]
    const currentIndex = players.findIndex(p => p.playing === true)
    if (currentIndex !== -1 && currentIndex !== targetIndex) {
      newPlayers[currentIndex].playing = false
      newPlayers[targetIndex].playing = true
    } else if (currentIndex !== -1) {
      newPlayers[targetIndex].playing = false
    } else {
      newPlayers[targetIndex].playing = true
    }
    setPlayers(newPlayers)
  }

  useEffect(() => {
    sources.forEach((source, i) => {
      players[i].playing ? source.audio.play() : source.audio.pause()
    })
  }, [sources, players])

  useEffect(() => {
    sources.forEach((source, i) => {
      source.audio.addEventListener('ended', () => {
        const newPlayers = [...players]
        newPlayers[i].playing = false
        setPlayers(newPlayers)
      })
    })
    return () => {
      sources.forEach((source, i) => {
        source.audio.removeEventListener('ended', () => {
          const newPlayers = [...players]
          newPlayers[i].playing = false
          setPlayers(newPlayers)
        })
      })
    }
  }, [])

  return [players, toggle]
}

const MultiPlayer = ({ recordings }) => {
  let urls = []
  for (let rec of recordings) {
    urls.push(rec.recording_url);
  }
  const [players, toggle] = useMultiAudio(recordings);

  return (
    <div>
      {players.map((player, i) => (
        <Player key={i} player={player} toggle={toggle(i)} />
      ))}
    </div>
  )
}

const Player = ({ player, toggle }) => (
  <div>
    <p>
      <button onClick={toggle}>&#9655; </button> {player.url.speaker_name}, {player.url.language} <br />
      <a href={player.url.speaker_bio_url} target={"_blank"}> Learn more about the speaker...</a>
    </p>
  </div>
)


export default MultiPlayer
