import { Grid, useTheme } from "@mui/material" 
import { Error as ErrorIcon } from "@mui/icons-material"

interface Props {
    description?: string
}

function EmptyItem({description = "There are no items here"}: Props) {
    const theme = useTheme()

    return (
        <Grid 
            alignSelf='center' 
            margin='auto' 
            display='flex' 
            flexDirection='column' 
            justifyContent='center' 
            alignItems='center'
            color={theme.palette.text.secondary}
        >
            <ErrorIcon sx={{fontSize: '128px'}}/>
            <p>{description}</p>
        </Grid>
    )
}

export default EmptyItem