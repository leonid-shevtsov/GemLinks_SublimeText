require 'rubygems'
require 'json'
require 'bundler'

begin
  gems = Bundler.load.specs
rescue Bundler::BundlerError => e
  STDERR.puts e.to_s
  exit -1
end

gem_info = gems.map do |gem|
  {
    name: gem.name,
    version: gem.version.to_s,
    summary: gem.summary,
    homepage_url: gem.homepage,
    path: gem.gem_dir,
    spec_path: gem.spec_file
  }
end.sort_by {|gem| gem[:name]}

puts gem_info.to_json

exit 0