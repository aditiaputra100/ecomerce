import { Box, Container, Stack, Typography } from "@mui/material"
import { APP_NAME } from "../config"

function Footer() {
    return (
        <footer>
            <Stack>
                <Container component={Stack} direction='row' py={4} spacing={4}>
                    <Stack>
                        <Box>
                            <Typography variant="h2">
                                {APP_NAME}
                            </Typography>
                            <Typography>
                                Let's shop beyond boundaries
                            </Typography>
                        </Box>
                        <Box>
                            
                        </Box>
                    </Stack>
                    <Stack>
                        <Typography fontWeight={700}>
                            {APP_NAME}
                        </Typography>
                    </Stack>
                    <Stack>
                        <Typography fontWeight={700}>
                            Guide and Help
                        </Typography>
                    </Stack>
                    
                </Container>
                <Stack borderTop='1px solid rgba(0, 0, 0, 0.1)' justifyContent='center' textAlign='center'>
                    <p>&copy; 2026 {APP_NAME}</p>
                </Stack>
            </Stack>
        </footer>
    )
}

export default Footer