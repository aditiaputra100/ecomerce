import { alpha, Button, Container, Grid, Skeleton, Stack, Typography, useTheme, Alert } from "@mui/material"
import Category from "./Category"
import { useCategory } from "../store/category"
import EmptyItem from "./EmptyItem"

function CategoryList() {
    const categories = useCategory((s) => s.categories)
    const isLoading = useCategory((s) => s.isLoading)
    const error = useCategory((s) => s.error)
    const isCategoriesEmpty = categories.length === 0

    const theme = useTheme()
    const categoryAlphas = [0.35, 0.45, 0.55, 0.65, 0.75, 0.85]

    return (
        <Container sx={{marginY: 4}}>
          <Stack justifyContent='space-between' alignItems='center' direction='row'>
            <Typography variant="h2" fontSize="1.5rem" fontWeight={700}>Belanja Sesuai Kategory</Typography>
            <Button disabled={isCategoriesEmpty} variant="text" color="secondary">
              Lihat semua
            </Button>

          </Stack>
          <Grid container spacing={2} marginTop={2} alignItems="stretch">
            {error && (
              <Grid size={{ xs: 12 }}>
                <Alert severity="error">
                  {error}
                </Alert>
              </Grid>
            )}
            {isLoading && (
              Array.from({length: 6}, (_, idx) => (
                <Grid size={{xs: 6, md: 2}} key={idx} sx={{ display: 'flex' }}>
                  <Skeleton variant="rounded" height={120} sx={{borderRadius: 4}}/>
                </Grid>
              ))
            )}
            {
             isCategoriesEmpty && !isLoading && !error && (
                <EmptyItem description="There are no categories here" />
              )
            }
            {categories.map((category, index) => (
              <Grid size={{xs: 6, md: 2}} key={category.name} sx={{ display: 'flex' }}>
                <Category
                  label={category.name}
                  bgColor={alpha(theme.palette.primary.main, categoryAlphas[index % categoryAlphas.length])}
                  icon={category.icon ?? undefined}
                />
              </Grid>
            ))}
          </Grid>
        </Container>
    )
}

export default CategoryList
