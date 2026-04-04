import { Box, useTheme } from "@mui/material"
import { useEffect, useState } from "react"

interface Props {
    initialSeconds?: number
}

function Timer({initialSeconds=3600} : Props) {
    const theme = useTheme()

    const [seconds, setSeconds] = useState(initialSeconds)

    useEffect(() => {
        if (seconds <= 0) return

        const interval = setInterval(() => {
            setSeconds((prev) => prev - 1)
        }, 1000)

        return () => clearInterval(interval)

    }, [seconds])

    const formatTime = (totalSeconds: number) => {
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;

        const pad = (num: number) => String(num).padStart(2, "0");

        return {
            hours: pad(hours),
            minutes: pad(minutes),
            seconds: pad(seconds),
        }
    }

    const time = formatTime(seconds)

    return (
        <Box display='flex' alignItems='center' gap={1}>
            <span 
            className='flash-sale-timer' 
            style={{
                backgroundColor: theme.palette.primary.main,
                color: theme.palette.primary.contrastText,
                fontWeight: 700
            }}
            >
            {time.hours}
            </span>
            <span>:</span>
            <span 
            className='flash-sale-timer'
            style={{
                backgroundColor: theme.palette.primary.main,
                color: theme.palette.primary.contrastText,
                fontWeight: 700
            }}
            >
            {time.minutes}
            </span>
            <span>:</span>
            <span 
            className='flash-sale-timer'
            style={{
                backgroundColor: theme.palette.primary.main,
                color: theme.palette.primary.contrastText,
                fontWeight: 700
            }}
            >
            {time.seconds}
            </span>
        </Box>
    )
}

export default Timer