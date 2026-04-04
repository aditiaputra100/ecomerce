import { alpha, Button, Container, Grid, Skeleton, Stack, Typography, useTheme } from "@mui/material"
import Category from "./Category"
import { useCategory } from "../store/category"

function CategoryList() {
    const categories = useCategory((state) => state.categories)
    const isLoading = useCategory((state) => state.isLoading)
    const error = useCategory((state) => state.error)

    const theme = useTheme()

    return (
        <Container sx={{marginY: 4}}>
          <Stack justifyContent='space-between' alignItems='center' direction='row'>
            <Typography variant="h5" fontWeight={700}>Belanja Sesuai Kategory</Typography>
            <Button variant="text" color="secondary">
              Lihat semua
            </Button>

          </Stack>
          <Grid container spacing={2} marginTop={2}>
            {isLoading && (
              Array.from({length: 6}, (_, idx) => (
                <Grid size={{xs: 6, md: 2}} key={idx}>
                  <Skeleton variant="rounded" height={100} sx={{borderRadius: 4}}/>
                </Grid>
              ))
            )}
            {categories.map((category) => (
              <Grid size={{xs: 6, md: 2}} key={category.name}>
                <Category label={category.name} bgColor={alpha(theme.palette.primary.main, Math.random())} icon={category.icon}/>
              </Grid>
            ))}
          </Grid>
        </Container>
    )
}

export default CategoryList