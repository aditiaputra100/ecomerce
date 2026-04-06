import { alpha, Button, Container, Grid, Skeleton, Stack, Typography, useTheme, Alert } from "@mui/material"
import {
  Error as ErrorIcon
} from '@mui/icons-material'
import Category from "./Category"
import { useCategory } from "../store/category"
import EmptyItem from "./EmptyItem"

function CategoryList() {
    const categories = useCategory((s) => s.categories)
    const isLoading = useCategory((s) => s.isLoading)
    const error = useCategory((s) => s.error)
    const isCategoriesEmpty = categories.length == 0

    const theme = useTheme()

    return (
        <Container sx={{marginY: 4}}>
          <Stack justifyContent='space-between' alignItems='center' direction='row'>
            <Typography variant="h5" fontWeight={700}>Belanja Sesuai Kategory</Typography>
            <Button disabled={isCategoriesEmpty} variant="text" color="secondary">
              Lihat semua
            </Button>

          </Stack>
          <Grid container spacing={2} marginTop={2}>
            {error && (
              <Grid size={{ xs: 12 }}>
                <Alert severity="error" icon={<ErrorIcon />}>
                  {error}
                </Alert>
              </Grid>
            )}
            {isLoading && (
              Array.from({length: 6}, (_, idx) => (
                <Grid size={{xs: 6, md: 2}} key={idx}>
                  <Skeleton variant="rounded" height={100} sx={{borderRadius: 4}}/>
                </Grid>
              ))
            )}
            {
             isCategoriesEmpty && !isLoading && (
                <EmptyItem description="There are no categories here" />
              )
            }
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