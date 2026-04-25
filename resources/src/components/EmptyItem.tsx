import { Stack, Typography, useTheme } from "@mui/material"
import { Error as ErrorIcon } from "@mui/icons-material"

interface Props {
    description?: string
}

function EmptyItem({ description = "There are no items here" }: Props) {
    const theme = useTheme()

    return (
        <Stack
            alignSelf="center"
            margin="auto"
            justifyContent="center"
            alignItems="center"
            color={theme.palette.text.secondary}
        >
            <ErrorIcon sx={{ fontSize: '128px' }} />
            <Typography variant="body1">{description}</Typography>
        </Stack>
    )
}

export default EmptyItem
