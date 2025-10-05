import CityClient from '../../../components/CityClient'

export default async function CityPage({ params }) {
  const { slug } = await params
  return <CityClient slug={slug} />
}
